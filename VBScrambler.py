import argparse
import random
import string

banner = r"""
____   ______________   _________                               ___.    .__
\   \ /   /\______   \ /   _____/  ____ _______ _____     _____ \_ |__  |  |    ____ _______
 \   Y   /  |    |  _/ \_____  \ _/ ___\\_  __ \\__  \   /     \ | __ \ |  |  _/ __ \\_  __ \
  \     /   |    |   \ /        \\  \___ |  | \/ / __ \_|  Y Y  \| \_\ \|  |__\  ___/ |  | \/
   \___/    |______  //_______  / \___  >|__|   (____  /|__|_|  /|___  /|____/ \___  >|__|
                   \/         \/      \/             \/       \/     \/            \/
        VBScrambler by GH: @Bobby-Tablez
        https://github.com/bobby-tablez/VBScrambler

"""
print(banner)

def scramble_vbscript(code, shift_num):
    obfuscated = ''.join(chr(ord(v) + shift_num) for v in code)
    code_len = len(obfuscated)

    # Fix double quotes if they're generated after the shift
    final_code = obfuscated.replace('"', '""')

    # Randomize variable name
    var_name = ''.join(random.choices(string.ascii_letters, k=4))

    # Generate the output
    result = (var_name + r' = "":for i = 1 to ' + f"{code_len}" + ": " + var_name +
              f" = {var_name} + chr(Asc(mid(\"{final_code}\",i,1)) - ({shift_num})):Next:Execute " + var_name + ":")

    return result

def scramble_javascript(code, shift_num):
    obfuscated = ''.join(chr(ord(v) + shift_num) for v in code)

    # Escape special characters for JavaScript string
    final_code = (obfuscated
                  .replace('\\', '\\\\')
                  .replace('"', '\\"')
                  .replace('\n', '\\n')
                  .replace('\r', '\\r')
                  .replace('\t', '\\t'))

    # Randomize variable name
    var_name = ''.join(random.choices(string.ascii_letters, k=4))

    # Generate the output with JavaScript deobfuscation
    result = (f"var {var_name}=\"\";for(var i=0;i<\"{final_code}\".length;i++)" +
              f"{{{var_name}+=String.fromCharCode(\"{final_code}\".charCodeAt(i)-{shift_num});}}eval({var_name});")

    return result

def main():

    parser = argparse.ArgumentParser(description="VBScrambler - Multi-language code obfuscator")
    parser.add_argument("-c", "--content", nargs=argparse.REMAINDER, help="Inline code to obfuscate.", default=[], required=False)
    parser.add_argument("-f", "--file", type=str, help="File to obfuscate.", required=False)
    parser.add_argument("-o", "--output", type=str, help="Output file to save the scrambled code to", required=False)
    parser.add_argument("-s", "--shift", type=int, help="Manually set the ROT/Shift number", required=False)
    parser.add_argument("-l", "--language", type=str, choices=['vbscript', 'javascript', 'vbs', 'js'],
                        default='vbscript', help="Language to obfuscate (vbscript/vbs or javascript/js)")

    args = parser.parse_args()

    # Normalize language input
    language = args.language.lower()
    if language in ['vbs', 'vbscript']:
        language = 'vbscript'
    elif language in ['js', 'javascript']:
        language = 'javascript'

    # Handle the various input types
    if args.content:
        code = ' '.join(args.content)
    elif args.file:
        try:
            with open(args.file, 'r') as file:
                code = file.read()
        except FileNotFoundError:
            print(f"Error: The file '{args.file}' does not exist.")
            return
    else:
        prompt = "Provide a VBScript one-liner (Mind your quotes!):" if language == 'vbscript' else "Provide JavaScript code to obfuscate:"
        code = input(prompt)

    if args.shift:
        shift_num = args.shift
    else:
        shift_num = random.randint(-5, 7) # Define range for byte shifts. This range seems to work well with most scripts. Increasing this could break the generated script

    # Scramble based on language
    if language == 'vbscript':
        result = scramble_vbscript(code, shift_num)
    else:
        result = scramble_javascript(code, shift_num)

    # Either save output as a file, or print it based on parameters used
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as file:
                file.write(result)
            print(f"\nContent saved to {args.output}\n")
        except IOError as e:
            print(f"\nError writing to file: {e}\n")
    else:
        print(f"\n{result}\n")

if __name__ == "__main__":
    main()
