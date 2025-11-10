#!/usr/bin/env python3
import gi

import main

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Pango
import subprocess
import threading
import os

# if you have your own main module calls, adapt these references
# import main

class App(Gtk.Window):
    def __init__(self):
        super().__init__(title="Server Manager")
        self.set_default_size(900, 540)
        # padding around whole window
        self.set_border_width(12)

        # Main layout: horizontal box (buttons left, logs right)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.add(hbox)

        # LEFT: Vertical button box (small buttons)
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        # give some margin so buttons are not stuck to the left edge of the window content area
        button_box.set_margin_start(6)
        button_box.set_margin_end(6)
        button_box.set_margin_top(6)
        button_box.set_margin_bottom(6)
        hbox.pack_start(button_box, False, False, 0)

        # Buttons (small fixed width)
        btn_width = 140
        get_btn = Gtk.Button(label="Get from GitHub")
        get_btn.set_size_request(btn_width, -1)
        get_btn.connect("clicked", self.on_get_clicked)
        button_box.pack_start(get_btn, False, False, 0)

        start_btn = Gtk.Button(label="Start Tomcat")
        start_btn.set_size_request(btn_width, -1)
        start_btn.connect("clicked", self.on_start_clicked)
        button_box.pack_start(start_btn, False, False, 0)

        stop_btn = Gtk.Button(label="Stop Tomcat")
        stop_btn.set_size_request(btn_width, -1)
        stop_btn.connect("clicked", self.on_stop_clicked)
        button_box.pack_start(stop_btn, False, False, 0)

        exit_btn = Gtk.Button(label="Exit")
        exit_btn.set_size_request(btn_width, -1)
        exit_btn.connect("clicked", self.confirm_exit)
        button_box.pack_start(exit_btn, False, False, 0)

        # put a small spacer at bottom so buttons don't stretch to fill everything
        button_box.pack_end(Gtk.Label(), True, True, 0)

        # RIGHT: Scrollable text output area
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        # monospace for logs
        self.textview.modify_font(Pango.FontDescription("monospace 10"))
        self.textbuffer = self.textview.get_buffer()

        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.add(self.textview)
        # store reference for scrolling
        self.log_scroll = scroll

        hbox.pack_start(scroll, True, True, 0)

        # Path relative to the Python file
        self.log_path = os.path.join(os.path.dirname(__file__), "logs", "log.out")
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        # ensure file exists
        open(self.log_path, "a", encoding="utf-8").close()

        # Open file in read mode and jump to end (so we only get new logs)
        self.log_file = open(self.log_path, "r", encoding="utf-8")
        self.log_file.seek(0, os.SEEK_END)

        # Setup a mark name we will use to scroll
        self.end_mark = None

        # Check every 300ms for new log lines
        GLib.timeout_add(300, self.check_log_updates)

        # If you need to run something on startup, do it here (commented out)
        main.runMini()


    def check_log_updates(self):
        """Read only newly appended lines from log file."""
        appended = False
        while True:
            line = self.log_file.readline()
            if not line:
                break
            self.log(line.rstrip())
            appended = True

        # if new lines appended, ensure we scroll (scroll happens inside log append)
        return True

    def log(self, text):
        """Append text to the text box safely from threads and auto-scroll to bottom."""
        def append_and_scroll():
            end_iter = self.textbuffer.get_end_iter()
            # insert text + newline
            self.textbuffer.insert(end_iter, text + "\n")
            # create/update mark at buffer end and scroll to it
            # use a named mark that follows the inserted text
            if self.end_mark is None:
                self.end_mark = self.textbuffer.create_mark("end_mark", self.textbuffer.get_end_iter(), True)
            else:
                # move existing mark to new end
                self.textbuffer.move_mark(self.end_mark, self.textbuffer.get_end_iter())
            # scroll_to_mark arguments: (mark, within_margin, use_align, xalign, yalign)
            # use_align=True and yalign=1.0 tries to align the mark at bottom.
            self.textview.scroll_to_mark(self.end_mark, 0.0, True, 0.0, 1.0)
            return False  # GLib.idle_add handler should return False to run once
        # schedule on main loop so it's safe from worker threads
        GLib.idle_add(append_and_scroll)

    def on_get_clicked(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Choose destination folder to clone into",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Select", Gtk.ResponseType.OK)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            folder = dialog.get_filename()
            dialog.destroy()
            self.log(f"Selected: {folder}")
            # Example placeholder fetch call:
            # replace URL with actual repo you want to clone
            self.run_command(["git", "clone", "https://github.com/example/repo.git", folder])
        else:
            dialog.destroy()

    def confirm_exit(self, _):
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Exit Application?",
        )
        dialog.format_secondary_text("Are you sure you want to exit?")

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self.exit(None)

    def exit(self, _):
        main.clean()
        self.close()
        Gtk.main_quit()

    def on_start_clicked(self, button):
        main.startTomcat(main.globalTomcatDir)

    def on_stop_clicked(self, button):
        main.stopTomcat(main.globalTomcatDir)

    def run_command(self, cmd):
        def worker():
            self.log(f"$ {' '.join(cmd)}")
            try:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                # non-blocking read of stdout lines; this yields lines as they arrive
                for line in p.stdout:
                    self.log(line.rstrip())
                p.wait()
                self.log(f"Process exited with {p.returncode}")
            except Exception as e:
                self.log(f"Error: {e}")
        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    win = App()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
