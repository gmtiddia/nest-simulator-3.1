#!/bin/sh

# static_code_analysis.sh
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.


# This shell script is part of the NEST Travis CI build and test environment.
# It performs the static code analysis and is invoked by 'build.sh'.
# The script is also executed when running 'check_code_style.sh' for
# a local static code analysis.
#
# NOTE: This shell script is tightly coupled to Python script
#       'extras/parse_travis_log.py'. 
#       Any changes to message numbers (MSGBLDnnnn) have effects on 
#       the build/test-log parsing process.
#

# Command line parameters.
RUNS_ON_TRAVIS=$1        # true or false, indicating whether the script is executed on Travis CI or runs local.
INCREMENTAL=$2           # true or false, user needs to confirm befor checking a source file.
FILE_NAMES=$3            # The list of files or a single file to be checked.
NEST_VPATH=$4            # The high level NEST build path.
VERA=$5                  # Name of the VERA++ executable.
CPPCHECK=$6              # Name of the CPPCHECK executable.
CLANG_FORMAT=$7          # Name of the CLANG-FORMAT executable.
PEP8=$8                  # Name of the PEP8 executable.

# PEP8 rules to ignore.
PEP8_IGNORES="E121,E123,E126,E226,E24,E704"
PEP8_IGNORES_EXAMPLES="${PEP8_IGNORES},E402"
PEP8_IGNORES_TOPO_MANUAL="${PEP8_IGNORES_EXAMPLES},E265"

# Print a message.
# The format of the message depends on whether the script is executed on Travis CI or runs local.
# print_msg "string1" "string2"
print_msg() {
  if $RUNS_ON_TRAVIS; then
    echo "$1$2"
  else
    echo "$2"
  fi
}

# Print version information.
VERA_VERS=`$VERA --version`
CPPCHECK_VERS=`$CPPCHECK --version | sed 's/^Cppcheck //'`
CLANG_FORMAT_VERS=`$CLANG_FORMAT --version`
PEP8_VERS=`$PEP8 --version`
print_msg "" ""
print_msg "MSGBLD0105: " "Following tools are in use:"
print_msg "MSGBLD0105: " "---------------------------"
print_msg "MSGBLD0105: " "VERA++       : $VERA_VERS"
print_msg "MSGBLD0105: " "CPPCHECK     : $CPPCHECK_VERS"
print_msg "MSGBLD0105: " "CLANG-FORMAT : $CLANG_FORMAT_VERS"
print_msg "MSGBLD0105: " "PEP8         : $PEP8_VERS"
print_msg "" ""

# Perfom static code analysis.
format_error_files=""
for f in $FILE_NAMES; do

  if [ ! -f "$f" ]; then
    print_msg "MSGBLD0110: " "$f is not a file or does not exist anymore."
    continue
  fi
  if ! $RUNS_ON_TRAVIS && $INCREMENTAL; then
    print_msg "" ""
    print_msg "" "Press [Enter] to continue.  (Static code analysis for file $f.)"
    read continue
  fi
  if $RUNS_ON_TRAVIS; then
    print_msg "MSGBLD0120: " "Perform static code analysis for file $f."
  fi

  case $f in
    *.h | *.c | *.cc | *.hpp | *.cpp )
      vera_failed=false
      cppcheck_failed=false
      clang_format_failed=false

      if $RUNS_ON_TRAVIS; then
        f_base=$NEST_VPATH/reports/`basename $f`
      else
        f_base=`basename $f`
      fi

      # VERA++
      print_msg "MSGBLD0130: " "Running VERA++ .....: $f"
      $VERA --profile nest $f > ${f_base}_vera.txt 2>&1
      if [ -s "${f_base}_vera.txt" ]; then
        vera_failed=true
        cat ${f_base}_vera.txt | while read line
        do
          print_msg "MSGBLD0135: " "[VERA] $line"
        done
      fi
      rm ${f_base}_vera.txt
      if $RUNS_ON_TRAVIS; then
        print_msg "MSGBLD0140: " "VERA++ for file $f completed."
      fi

      # CPPCHECK
      print_msg "MSGBLD0150: " "Running CPPCHECK ...: $f"
      $CPPCHECK --enable=all --inconclusive --std=c++03 --suppress=missingIncludeSystem $f > ${f_base}_cppcheck.txt 2>&1
      # Remove the header, the first line.
      tail -n +2 "${f_base}_cppcheck.txt" > "${f_base}_cppcheck.tmp" && mv "${f_base}_cppcheck.tmp" "${f_base}_cppcheck.txt"
      if [ -s "${f_base}_cppcheck.txt" ]; then
        cppcheck_failed=true
        cat ${f_base}_cppcheck.txt | while read line
        do
          print_msg "MSGBLD0155: " "[CPPC] $line"
        done
      fi
      rm ${f_base}_cppcheck.txt
      if $RUNS_ON_TRAVIS; then
        print_msg "MSGBLD0160: " "CPPCHECK for file $f completed."
      fi

      # CLANG-FORMAT
      print_msg "MSGBLD0170: " "Running CLANG-FORMAT: $f"
      # Create a clang-format formatted temporary file and perform a diff with its origin.
      file_formatted="${f_base}_formatted.txt"
      file_diff="${f_base}_diff.txt"
      $CLANG_FORMAT $f > $file_formatted
      diff $f $file_formatted > $file_diff 2>&1
      if [ -s "$file_diff" ]; then
        clang_format_failed=true
        cat $file_diff | while read line
        do
          print_msg "MSGBLD0175: " "[DIFF] $line"
        done
      fi
      rm $file_formatted
      rm $file_diff
      if $RUNS_ON_TRAVIS; then
        print_msg "MSGBLD0180: " "CLANG-FORMAT for file $f completed."
      fi

      # Add the file to the list of files with format errors.
      if $vera_failed || $cppcheck_failed || $clang_format_failed; then
        format_error_files="$format_error_files $f"
      fi
      ;;

    *.py )
      # PEP8
      print_msg "MSGBLD0190: " "Running PEP8 .......: $f"
      case $f in
        *user_manual_scripts*)
          IGNORES=$PEP8_IGNORES_TOPO_MANUAL
          ;;
        *examples*)
          IGNORES=$PEP8_IGNORES_EXAMPLES
          ;;
        *)
          IGNORES=$PEP8_IGNORES
          ;;
      esac
      if ! pep8_result=`$PEP8 --ignore=$PEP8_IGNORES $f` ; then
        printf '%s\n' "$pep8_result" | while IFS= read -r line
        do
          print_msg "MSGBLD0195: " "[PEP8] $line"
        done
        # Add the file to the list of files with format errors.
        format_error_files="$format_error_files $f"
      fi
      if $RUNS_ON_TRAVIS; then
        print_msg "MSGBLD0200: " "PEP8 check for file $f completed."
      fi
      ;;

    *)
      print_msg "MSGBLD0210: " "Skipping ...........: $f  (not a C/C++/Python file)"
      continue
  esac
done

if $RUNS_ON_TRAVIS; then
  if [ "x$format_error_files" != "x" ]; then
    for f in $format_error_files; do
      print_msg "MSGBLD0220: " "Formatting error in file: $f"
    done
  fi
else
  if [ "x$format_error_files" != "x" ]; then
    print_msg "" ""
    print_msg "" "+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +"
    print_msg "" "+                 TRAVIS CI MAY REPORT FORMAT ERRORS !                        +"
    print_msg "" "+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +"
    for f in $format_error_files; do
      print_msg "" "Formatting error in file: $f"
    done
    print_msg "" "Please work through the [VERA], [CPPC], [PEP8] and [DIFF] messages and correct your source code accordingly."
    print_msg "" "- On C/C++ files, perform '$CLANG_FORMAT -i <filename>'."
    print_msg "" "- On Python files, perform 'pep8ify -w <filename>'."
    print_msg "" "+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +"
  else
    print_msg "" ""
    print_msg "" "+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +"
    print_msg "" "+             STATIC CODE ANALYSIS TERMINATED SUCESSFULLY !                   +"
    print_msg "" "+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +"
  fi
fi
