#!/bin/bash

# Function to parse YAML file
parse_yaml() {
   local prefix=$2
   local s='[[:space:]]*'
   local w='[a-zA-Z0-9_]*'
   local fs
   fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\):|\1|" \
        -e "s|^$s\($w\)$s:$s[\"\']\(.*\)[\"\']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^$s\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p" "$1" |
   awk -F"$fs" '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'", vn, $2, $3);
      }
   }'
}

# Function to display available processes and their parameters
show_help() {
  config_file=$1

  echo "Available processes and their parameters:"

  # Parse the YAML file
  eval "$(parse_yaml "$config_file" "config_")"

  # Extract process names
  for process in $(compgen -A variable | grep -E '^config_processes_[^_]+$'); do
    local process_name="${process#config_processes_}"
    echo "Process: ${process_name}"
    local script_var="config_processes_${process_name}_script"
    local script="${!script_var}"
    echo "  Script: ${script}"

    echo "  Parameters:"
    for param in $(compgen -A variable | grep -E "^config_processes_${process_name}_parameters_[0-9]+_name$"); do
      local param_index="${param#config_processes_${process_name}_parameters_}"
      param_index="${param_index%_name}"
      local param_name="${!param}"
      local param_desc_var="config_processes_${process_name}_parameters_${param_index}_description"
      local param_desc="${!param_desc_var}"
      echo "    --${param_name}: ${param_desc}"
    done
    echo
  done
}

# Get the directory of this script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if at least 1 argument is provided (config_file)
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 config_file [process_name] [input1=value1 ... inputN=valueN]"
  echo "Use '--help' as the process_name to see available processes and their parameters."
  exit 1
fi

# Extract the configuration file
config_file=$1

# Check if help is requested
if [ "$2" == "--help" ]; then
  show_help "$config_file"
  exit 0
fi

# Check if at least 2 arguments are provided (config_file and process_name)
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 config_file [process_name] [input1=value1 ... inputN=valueN]"
  echo "Use '--help' as the process_name to see available processes and their parameters."
  exit 1
fi

# Extract the process name
process_name=$2

# Shift to get the list of inputs
shift 2

# Parse the YAML file
eval "$(parse_yaml "$config_file" "config_")"

# Read the Python environment and script location from the parsed YAML configuration
python_env="${config_python_env}"
script_location="${config_script_location}"

# Get the corresponding Python script for the process name
script_name_var="config_processes_${process_name}_script"
script_name="${!script_name_var}"

# Check if the script name was found
if [ -z "$script_name" ]; then
  echo "Error: No script found for process name '$process_name'"
  exit 1
fi

# Construct the command to run the Python script
python_command="$python_env/bin/python $script_location/$script_name"

# Add all named inputs to the command
for input in "$@"
do
  python_command+=" --${input}"
done

# Run the command
echo "Running command: $python_command"
$python_command
