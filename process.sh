#!/bin/bash

input_dir=$(dirname "$1")
input_filename=$(basename "$1")

input_dir_abs=$(readlink -f "$input_dir")
output_dir_abs=$(readlink -f "$output_dir")
input_file_abs=$(readlink -f "$input_dir/$input_filename")

touch "$2"
output_file_abs=$(readlink -f "$2")
template_file_abs=$(readlink -f ./template.plain)
lua_file_abs=$(readlink -f ./process.lua)

ECHO $output_file_abs
cd "$input_dir"

pandoc -f latex -t plain "$input_file_abs" --template="$template_file_abs" --lua-filter="$lua_file_abs" --columns=999999 -o "$output_file_abs"
cd -
