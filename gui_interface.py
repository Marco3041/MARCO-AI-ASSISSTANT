# gui_interface.py
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import queue
import time # For slight delays to make UI updates smoother
import speech_recognition as sr # <--- This line is essential for sr.Microphone() and sr exceptions

# Import functions/data from your existing modules
from tts_stt import speak, recognize_speech
from assistant_actions import process_command
import config # To access CONVERSATION_HISTORY and manage shared state


class MarcoGUI:
    def __init__(self, master):
        self.master = master
        master.title("Marco AI Assistant - The Chosen One")
        master.geometry("800x600") # Increased size for better appearance
        master.resizable(False, False) # Make window non-resizable for fixed layout

        self.command_queue = queue.Queue() # To send commands to processing thread
        self.response_queue = queue.Queue() # To receive responses from processing thread

        self.current_input_mode = "text" # Default to text input
        self.listening_for_activation = True # For voice activation in GUI

        # --- Styling ---
        master.tk_setPalette(background='#36454F', foreground='white',
                             activeBackground='#4B5B67', activeForeground='white')
        
        self.font_large = ('Arial', 12)
        self.font_medium = ('Arial', 10)

        # --- Widgets ---
        self.create_widgets()
        
        # --- Start a background thread for AI processing ---
        self.processing_thread = threading.Thread(target=self.process_commands_from_queue, daemon=True)
        self.processing_thread.start()

        # --- Start a periodic check for responses ---
        self.master.after(100, self.check_response_queue)
        
        # Display initial conversation history
        self.update_display_with_history()

    def create_widgets(self):
        # Frame for controls
        control_frame = tk.Frame(self.master, bg='#2F4F4F', padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        # Input Mode Selector
        self.mode_label = tk.Label(control_frame, text="Input Mode:", font=self.font_medium, bg='#2F4F4F', fg='white')
        self.mode_label.pack(side=tk.LEFT, padx=(0, 10))

        self.mode_var = tk.StringVar(self.master)
        self.mode_var.set("Text") # Default value
        self.mode_var.trace_add("write", self.on_mode_change) # Call on_mode_change when mode changes

        mode_options = ["Text", "Voice"]
        self.mode_menu = tk.OptionMenu(control_frame, self.mode_var, *mode_options)
        self.mode_menu.config(font=self.font_medium, bg='#556B2F', fg='white', activebackground='#6B8E23')
        self.mode_menu["menu"].config(bg='#556B2F', fg='white', activebackground='#6B8E23')
        self.mode_menu.pack(side=tk.LEFT, padx=(0, 20))

        # --- Text Input Area ---
        text_input_frame = tk.Frame(self.master, bg='#36454F', padx=10, pady=5)
        text_input_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.command_entry = tk.Entry(text_input_frame, font=self.font_large, bg='#4B5B67', fg='white', insertbackground='white')
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.command_entry.bind("<Return>", self.send_text_command) # Bind Enter key

        self.send_button = tk.Button(text_input_frame, text="Send", command=self.send_text_command,
                                     font=self.font_medium, bg='#556B2F', fg='white', activebackground='#6B8E23')
        self.send_button.pack(side=tk.LEFT)

        self.voice_button = tk.Button(text_input_frame, text="Speak", command=self.start_voice_input,
                                     font=self.font_medium, bg='#556B2F', fg='white', activebackground='#6B8E23')
        self.voice_button.pack(side=tk.LEFT, padx=(10,0))
        
        # Initially hide/show buttons based on default mode
        self.update_input_widgets()


        # --- Conversation Display Area ---
        self.display_text = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, font=self.font_medium,
                                                     bg='#2F4F4F', fg='white', insertbackground='white',
                                                     state='disabled', padx=10, pady=10)
        self.display_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Status Bar ---
        self.status_label = tk.Label(self.master, text="Ready.", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                     font=('Arial', 9), bg='#36454F', fg='lightgray')
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def on_mode_change(self, *args):
        self.current_input_mode = self.mode_var.get().lower()
        self.update_input_widgets()
        self.status_label.config(text=f"Switched to {self.current_input_mode} mode.")
        if self.current_input_mode == "voice":
            speak("Switched to voice input mode. Say 'Marco' to activate.")
            self.listening_for_activation = True # Reset activation for voice mode

    def update_input_widgets(self):
        if self.current_input_mode == "text":
            self.command_entry.config(state='normal')
            self.send_button.config(state='normal')
            self.voice_button.config(state='disabled')
        else: # voice mode
            self.command_entry.config(state='disabled')
            self.send_button.config(state='disabled')
            self.voice_button.config(state='normal')

    def update_display(self, message):
        self.display_text.config(state='normal')
        self.display_text.insert(tk.END, message + "\n")
        self.display_text.see(tk.END) # Scroll to the bottom
        self.display_text.config(state='disabled')

    def update_display_with_history(self):
        self.display_text.config(state='normal')
        self.display_text.delete(1.0, tk.END) # Clear existing text
        for entry in config.CONVERSATION_HISTORY:
            role = "You" if entry["role"] == "user" else "Marco"
            self.display_text.insert(tk.END, f"{role}: {entry['content']}\n")
        self.display_text.see(tk.END)
        self.display_text.config(state='disabled')

    def send_text_command(self, event=None):
        if self.current_input_mode != "text":
            messagebox.showwarning("Input Mode Error", "Please switch to 'Text' input mode to type commands.")
            return

        command = self.command_entry.get()
        self.command_entry.delete(0, tk.END)
        if command:
            self.update_display(f"You: {command}")
            self.status_label.config(text="Processing typed command...")
            self.command_queue.put(command) # Put command into queue for background processing
        else:
            self.status_label.config(text="No command entered.")

    def start_voice_input(self):
        if self.current_input_mode != "voice":
            messagebox.showwarning("Input Mode Error", "Please switch to 'Voice' input mode to use voice commands.")
            return
            
        self.status_label.config(text="Listening for voice...")
        # Disable voice button while listening to prevent multiple threads
        self.voice_button.config(state='disabled')
        self.master.update_idletasks() # Force UI update immediately

        # Start listening in a new thread
        threading.Thread(target=self._listen_for_voice_command, daemon=True).start()

    def _listen_for_voice_command(self):
        r = config.get_recognizer()
        if not r:
            self.response_queue.put("Recognizer not initialized.")
            return

        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)

                if self.listening_for_activation:
                    self.status_label.config(text="Say 'Marco' to activate...")
                    audio_data = r.listen(source, timeout=10, phrase_time_limit=7)
                    word = recognize_speech(audio_data)
                    self.update_display(f"Heard activation attempt: '{word}'")

                    if "marco" in word:
                        self.response_queue.put("The Chosen One is Active. Your command, please.")
                        self.listening_for_activation = False
                        # Now listen for the actual command
                        self._listen_for_actual_command()
                    else:
                        self.response_queue.put("Activation word not detected. Say 'Marco' again or switch mode.")
                        self.master.after(10, lambda: self.voice_button.config(state='normal')) # Re-enable button safely
                        self.master.after(10, lambda: self.status_label.config(text="Ready. (Voice Mode)"))
                        self.listening_for_activation = True # Keep listening for activation
                else:
                    # Already activated, listen for command directly
                    self._listen_for_actual_command()

        except sr.UnknownValueError:
            self.response_queue.put("Voice command not clearly understood. Please try again.")
            self.listening_for_activation = False # Assume it's a command after activation
            self.master.after(10, lambda: self.voice_button.config(state='normal'))
            self.master.after(10, lambda: self.status_label.config(text="Ready. (Voice Mode)"))
        except sr.WaitTimeoutError:
            self.response_queue.put("No speech detected within the timeout. Say 'Marco' to activate or give command.")
            self.listening_for_activation = True # Go back to activation state
            self.master.after(10, lambda: self.voice_button.config(state='normal'))
            self.master.after(10, lambda: self.status_label.config(text="Ready. (Voice Mode)"))
        except Exception as e:
            self.response_queue.put(f"An unexpected error during voice input: {e}")
            self.master.after(10, lambda: self.voice_button.config(state='normal'))
            self.master.after(10, lambda: self.status_label.config(text="Ready. (Voice Mode)"))


    def _listen_for_actual_command(self):
        r = config.get_recognizer()
        try:
            self.status_label.config(text="Listening for command...")
            
            # --- FIX APPLIED HERE ---
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5) 
                audio_data = r.listen(source, timeout=10, phrase_time_limit=8)
            # --- END FIX ---

            command = recognize_speech(audio_data)
            self.update_display(f"You: {command}")

            if command:
                self.status_label.config(text="Processing voice command...")
                self.command_queue.put(command) # Put command into queue
            else:
                self.response_queue.put("Command not recognized. Please try again.")

        except sr.UnknownValueError:
            self.response_queue.put("Command not clearly understood. Please try again.")
        except sr.WaitTimeoutError:
            self.response_queue.put("No command received. Returning to activation state.")
            self.listening_for_activation = True
        except Exception as e:
            self.response_queue.put(f"An error occurred while getting command: {e}")
        finally:
            self.master.after(10, lambda: self.voice_button.config(state='normal')) # Re-enable button safely
            self.master.after(10, lambda: self.status_label.config(text="Ready. (Voice Mode)"))


    def process_commands_from_queue(self):
        """
        Runs in a separate thread to process commands from the command_queue.
        """
        while True:
            try:
                command = self.command_queue.get(timeout=1.0) # Wait for a command
                if command:
                    # Call the core processing function
                    result = process_command(command)
                    if result == "exit_program":
                        self.master.quit() # Exit Tkinter application
                        break # Stop this thread

                    # After command processing, ensure display is updated with Marco's response
                    # This is crucial for LLM responses and direct actions
                    self.master.after(100, self.update_display_with_history) # Schedule update on main thread
                    self.response_queue.put("Command processed.") # Indicate completion
                self.command_queue.task_done()
            except queue.Empty:
                time.sleep(0.1) # Small sleep if queue is empty to avoid busy-waiting
            except Exception as e:
                self.response_queue.put(f"Error in processing thread: {e}")
                self.command_queue.task_done()

    def check_response_queue(self):
        """
        Checks the response queue periodically and updates the GUI.
        Runs in the main Tkinter thread.
        """
        try:
            message = self.response_queue.get_nowait()
            if message == "Command processed.":
                self.status_label.config(text="Ready.")
            else:
                self.status_label.config(text=message)
                speak(message) # Speak the status messages from the queue too
            self.response_queue.task_done()
        except queue.Empty:
            pass # No message in queue
        except Exception as e:
            print(f"Error checking response queue: {e}")
        finally:
            self.master.after(100, self.check_response_queue) # Check again after 100ms