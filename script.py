#!/usr/bin/env python

from optparse import OptionParser
import os, re, sys

class Converter:
    
    def __init__(self, file_path):
        
        """
        Dictionaries and lists of various purposes.
        """
        # List of BWW elements to ignore when converting.
        self.ignored_elements = (
            "sharpf",
            "sharpc",
            "space",
            "&"
        )
        
        # Dictionary mapping BWW note values to LilyPond note values.
        self.note_dictionary = {
            "lg":"G",
            "la":"a",
            "b":"b",
            "c":"c",
            "d":"d",
            "e":"e",
            "f":"f",
            "hg":"g",
            "g":"g", # Used for high G grace notes.
            "ha":"A",
            "t":"A" # Used for high A grace notes.
        }
        
        # Dictionary mapping BWW elements to their LilyPond equivalents.
        self.transpose_dict = {
            "!":"\\bar \"|\"\n",
            "!I":"\\bar \"|.\" \\break \n",
            "''!I":"\\bar \":|\" \\break\n",
            "I!''":"\\bar \"|:\"",
            "I!":"\\bar \"|.\"",
            "!t":"\\bar \"|\" \\break\n\n",
            "_'":"\\set Score.repeatCommands = #'((volta #f)) \\bar \"|\"\n",
            "thrd":"\\thrwd",
            "gbr":"\\gbirl",
            "brl":"\\wbirl",
            "abr":"\\birl",
            "lgstd":"\\dbld",
            "gste":"\\slure",
            "grp":"\\grip",
            "tar":"\\taor",
            "gstd":"\\slurd",
            "tdbf":"\\tdblf",
            "tdblg":"\\tdblG",
            "lhstd":"\\Gthrwd"
        }
        
        """
        Regular expressions for recognizing certain elements.
        """
        # Regex for a time signature.
        self.time_signature_regex = re.compile("([0-9])_([0-9])")
        
        # Regex for a melody note.
        self.melody_note_regex = re.compile("(?P<note>[A-Z]+)(?P<dir>[a-z]*)_(?P<time>[0-9]{1,2})")
        
        # Regex for a grace note.
        self.grace_note_regex = re.compile("([h|l]*[abcdefgt])g")
        
        # Regex for a doubling.
        self.doubling_regex = re.compile("^db([h|l]*[g|a|b|c|d|e|f]{1})")
        
        # Regex for a half-doubling.
        self.half_doubling_regex = re.compile("^hdb([h|l]*[g|a|b|c|d|e|f]{1})")
        
        # Regex for a strike.
        self.strike_regex = re.compile("str([h|l]*[abcdefg])")
        
        # Regex for a dot.
        self.dot_regex = re.compile("'[h|l]*[abcdefg]")
        
        # Regex for a slur.
        self.slur_regex = re.compile("\^(?P<note_count>[0-9])(?P<end_note>[a-z]*)")
        
        # Regex for a sub repeat.
        self.sub_repeat_regex = re.compile("'([0-9]+)")
        
        # Regex for a lilypond note.
        self.lilypond_note_regex = re.compile("[abcdefgAG][0-9]{1,2}")
        
        """
        Converter state variables.
        """
        # Stores the position of the most recent melody note added.
        # Used for applying dots to notes.
        self.previous_melody_note_index = 0
        
        # Remembers whether a slur tie has been seen.
        slur_tie_pending = False
        
        # Remembers if a note group has been started.
        self.in_note_group = False
        
        """
        Input file information.
        """
        abs_file = os.path.join(os.getcwd(),file_path)
        file_name = os.path.basename(abs_file)
        (self.name, ext) = file_name.split(".")
        
        if os.path.isfile(abs_file):
            self.original_file = abs_file
            self.file_dir = os.path.dirname(abs_file)
        else:
            raise Exception(bww_file_path+" is not a file")
    
    def run(self):
        
        input_file = open(self.original_file, "r")
        self.input_text = input_file.read()
        input_file.close()
        self.get_metadata()
        self.get_elements()
        self.translate_elements()
        self.calculate_partial()
    
    def get_metadata(self):
        
        quote_regex = re.compile("\"(.*)\"")
        metadata = quote_regex.findall(self.input_text)
        
        self.metadata = {}
        self.metadata["title"] = metadata[0]
        self.metadata["meter"] = metadata[1]
        self.metadata["author"] = metadata[2]
    
    def get_elements(self):
        
        """
        Regex to find all music notation, from the first ampersand
        to the last ending barline.
        """
        notes_regex = re.compile("&.*!I", re.S)
        notes_result = notes_regex.search(self.input_text)
        try:
            notes = notes_result.group()
        except:
            self.quit("No music elements found. Make sure this is a valid bww file.")
        self.elements = notes.split()
    
    def translate_elements(self):
        
        self.lilypond_elements = []
        for element in self.elements:
            self.translate(element)
    
    def translate(self, element):
        
        # Handle time signatures.
        time_signature_match = self.time_signature_regex.search(element)
        if time_signature_match:
            self.add_time_signature(time_signature_match)
            return
        
        # Handle melody notes.
        melody_note_match = self.melody_note_regex.search(element)
        if melody_note_match:
            self.add_melody_note(melody_note_match)
            return
        
        # Handle grace notes.
        grace_note_match = self.grace_note_regex.search(element)
        if grace_note_match:
            self.add_grace_note(grace_note_match)
            return
        
        # Handle doublings.
        doubling_match = self.doubling_regex.search(element)
        if doubling_match:
            self.add_doubling(doubling_match)
            return
        
        # Handle half-doublings.
        half_doubling_match = self.half_doubling_regex.search(element)
        if half_doubling_match:
            self.add_half_doubling(half_doubling_match)
            return
        
        # Handle strikes.
        strike_match = self.strike_regex.search(element)
        if strike_match:
            self.add_strike(strike_match)
            return
        
        # Handle dotted notes.    
        dot_match = self.dot_regex.search(element)
        if dot_match:
            self.add_dot(dot_match)
            return
        
        # Handle slurs.
        slur_match = self.slur_regex.search(element)
        if slur_match:
            self.add_slur(slur_match)
            return
        
        # Handle slur ties.
        if element == "^ts":
          self.slur_tie_pending = True
          return
        
        # Handle repeats.
        sub_repeat_match = self.sub_repeat_regex.search(element)
        if sub_repeat_match:
            self.add_sub_repeat(sub_repeat_match)
            return
        
        # Handle ignored elements.
        if element in self.ignored_elements:
            return
        
        # If the element is an start double, check if the previous element was an end double.
        if len(self.lilypond_elements):
            last_element = self.lilypond_elements[-1]
            if element == "I!''" and ":|" in last_element:
                # If so, replace the last element with a double double
                self.lilypond_elements[-1] = "\\bar \":|:\" \\break\n\n"
                return
        
        # Handle elements in the transposition dictionary.
        try:
            dict_result = self.transpose_dict[element]
            if dict_result:
                self.lilypond_elements.append(dict_result)
                return
        except KeyError:
            print "Unparsed: " + element
    
    def add_time_signature(self, time_signature_match):
        time_signature = "%s/%s" % (time_signature_match.group(1), time_signature_match.group(2))
        lilypond_time_signature = "\\time %s\n" % time_signature
        self.lilypond_elements.append(lilypond_time_signature)
        
    def add_melody_note(self, melody_note_match):
        note = melody_note_match.group("note")
        time = melody_note_match.group("time")
        direction = melody_note_match.group("dir")
        lilypond_melody_note = self.get_lilypond_note(note, "melody note") + time
        if lilypond_melody_note:
            # Add the note.
            self.lilypond_elements.append(lilypond_melody_note)
            
            # Store index of the note we just added.
            self.previous_melody_note_index = len(self.lilypond_elements) - 1
            
            # Perform note grouping logic.
            if direction == "r" and not self.in_note_group:
                # Every time a "r" is seen, start a note group.
                self.in_note_group = True
                self.lilypond_elements.append("[")
            elif direction == "l":
                if self.in_note_group:
                    self.in_note_group = False
                    self.lilypond_elements.append("]")
                    self.last_note_group_close = len(self.lilypond_elements) - 1
                else:
                    # Delete the last note group close.
                    del(self.lilypond_elements[self.last_note_group_close])
                    self.previous_melody_note_index -= 1
                    self.lilypond_elements.append("]")

    def add_grace_note(self, grace_note_match):
        note = self.get_lilypond_note(grace_note_match.group(1), "grace note")
        if note:
            lilypond_grace_note = "\\gr%s" % note
            self.lilypond_elements.append(lilypond_grace_note)
    
    def add_doubling(self, doubling_match):
        note = self.get_lilypond_note(doubling_match.group(1), "doubling")
        if note:
            doubling = "\\dbl%s" % note
            self.lilypond_elements.append(doubling)
    
    def add_half_doubling(self, half_doubling_match):
        note = self.get_lilypond_note(half_doubling_match.group(1), "half-doubling")
        if note:
            half_doubling = "\\hdbl%s" % note
            self.lilypond_elements.append(half_doubling)
    
    def add_strike(self, strike_match):
        
        note = self.get_lilypond_note(strike_match.group(1), "strike")
        if note:
            # Strikes on low G, high G, or low A are just gracenotes.
            if note == "G" or note == "g" or note == "a":
                strike = "\\gr%s" % note
            else:
                # Otherwise it is an actual slur.
                strike = "\\slur%s" % note
            self.lilypond_elements.append(strike)
    
    def add_dot(self, dot_match):
        try:
            note = self.lilypond_elements[self.previous_melody_note_index]
            if note[-1] == "~":
                self.lilypond_elements[self.previous_melody_note_index].replace("~",".~")
            else:
                self.lilypond_elements[self.previous_melody_note_index] += "."
        except IndexError:
            print "Invalid dot placement."
    
    def add_slur(self, slur_match):
        
        slur_length = int(slur_match.group("note_count"))
        end_note = slur_match.group("end_note")
        
        note_count = 0
        index = len(self.lilypond_elements) - 1
        while note_count < slur_length:
            element = self.lilypond_elements[elem_index]

            # If the element is a melody note, increment the note count.
            if self.lilypond_note_regex.search(element):
                note_count += 1

            # Decrement the index to move backwards.
            index -= 1
        
        # Start the slur just after the start note.
        self.lilypond_elements.insert(elem_index + 1,"(")
        
        # End the slur.
        self.lilypond_elements.append(")")
    
    def add_sub_repeat(self, sub_repeat_match):
        sub_repeat_number = sub_repeat_match.group(1)
        sub_repeat = "\\set Score.repeatCommands = #'((volta \"%s\")) " % sub_repeat_number
        self.lilypond_elements.append(sub_repeat)

    def get_lilypond_note(self, note, purpose=""):
        note = note.lower()
        try:
            return self.note_dictionary[note]
        except KeyError:
            message = "Unknown note value discovered: %s" % note
            if purpose != "":
                message = "%s\n\tFor: %s" % (message, purpose)
            print message
            return None
            
    def calculate_partial(self):
        
        index = 0
        first_bar_index = None
        second_bar_index = None
        
        # Get all notes between the first two bar elements.
        while index < len(self.lilypond_elements) and (first_bar_index == None or second_bar_index == None):
            element = self.lilypond_elements[index]
            if "bar" in element:
                if first_bar_index == None:
                    first_bar_index = index
                elif second_bar_index == None:
                    second_bar_index = index
            index += 1
        
        partial_notes = self.lilypond_elements[first_bar_index + 1:second_bar_index]
        
        partial_duration = 0
        for element in partial_notes:
            match = self.lilypond_note_regex.search(element)
            if match:
                duration = 1 / float(match.group(0)[1:])
                if "." in element:
                    duration *= 1.5
                partial_duration += duration
        
        if partial_duration > 0:
            partial_text = "\\partial %d" % (1 / partial_duration)
            self.lilypond_elements.insert(first_bar_index + 1, partial_text)
        
    def create_output_file(self):
        output_file = os.path.join(self.file_dir,self.name+".ly")
        file_handle = open(output_file,"w")
        text = self.get_lilypond_text()
        file_handle.write(text)
        file_handle.close()
        return output_file
    
    def get_lilypond_text(self):
        tune_text = " ".join(self.lilypond_elements)
    
        lilypond_text = '''
\\include "bagpipe.ly"
\\layout {
  indent = 0.0\\cm
  \\context { \\Score \\remove "Bar_number_engraver" }
}

\\header {
  title = "%s"
  meter = "%s"
  arranger = "%s"
  tagline = ""
}

{
  \\hideKeySignature
  %s
}''' % (self.metadata["title"],
        self.metadata["meter"],
        self.metadata["author"],
        tune_text)
    
        return lilypond_text
    
    def quit(self, message=None):
        if message is not None:
            print message
        sys.exit()


if __name__ == "__main__" :
    
    parser = OptionParser()
    parser.add_option("-i", "--in", dest="input_file_name",
        help="the FILE to convert", metavar="FILE")
    
    (options, args) = parser.parse_args()
    
    if options.input_file_name != None:
        converter = Converter(options.input_file_name)
        converter.run()
        new_file = converter.create_output_file()
    
    else:
        parser.print_help()

sys.exit()
