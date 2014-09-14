#!/bin/bash

[ -f "$HOME/.path_helper" ] && source "$HOME/.path_helper"

## so we don't blow up later in this file in case we didn't find .path_helper
res="$(type -t path_prepend > /dev/null 2>&1)"
if [ "$?" -ne 0 -o "$res" != "function" ]; then
    path_prepend () {
        PATH="$1:$PATH"
    }
fi
res="$(type -t path_append > /dev/null 2>&1)"
if [ "$?" -ne 0 -o "$res" != "function" ]; then
    path_append () {
        PATH="$PATH:$1"
    }
fi

# pip should only run if there is a virtualenv currently activated
export PIP_REQUIRE_VIRTUALENV=true
# cache pip-installed packages to avoid re-downloading
export PIP_DOWNLOAD_CACHE=$HOME/.pip/cache
## run the default (no virtualenv) pip
syspip () {
    PIP_REQUIRE_VIRTUALENV=""
    pip "$@"
}

path_prepend "/usr/local/sbin"
path_prepend "/usr/local/bin"

misc_paths[${#misc_paths[@]}]="$HOME/bin"
misc_paths[${#misc_paths[@]}]="$HOME/bin/aws"
misc_paths[${#misc_paths[@]}]="$HOME/sandbox/mydba-tools"

for mp in ${misc_paths[@]}
do
    [ -d "$mp" ] && path_append "$mp"
done

export CLICOLOR=0

## AWS STUFF
AMI_TOOLS_DIR="$HOME/bin/ec2-ami-tools-1.5.0.0"

export JAVA_HOME="/System/Library/Java/JavaVirtualMachines/1.6.0.jdk/Contents/Home"
export AWS_AUTO_SCALING_HOME="$HOME/bin/aws-autoscaling/AutoScaling-1.0.61.4"
export AWS_CREDENTIAL_FILE="$HOME/bin/aws-autoscaling/aws-creds"
export EC2_HOME="$HOME/bin/ec2-api-tools-1.6.12.2"

path_append "$AWS_AUTO_SCALING_HOME/bin"
path_append "$EC2_HOME/bin:$AMI_TOOLS_DIR/bin"

[ -f "$HOME/.aws/config" ] && {
    a_key="$(awk -F= ' $1 ~/^aws_access_key_id/ { print $2 } ' $HOME/.aws/config | xargs)"
    s_key="$(awk -F= ' $1 ~/^aws_secret_access_key/ { print $2 } ' $HOME/.aws/config | xargs)"

    [ -n "$a_key" ] && export AWS_ACCESS_KEY="$a_key"
    [ -n "$s_key" ] && export AWS_SECRET_KEY="$s_key"
}

## DOCKER STUFF
export DOCKER_HOST=tcp://localhost:4243

##  .                                     .  ##
## /!\ Don't manipulate PATH beyond this /!\ ##
export PATH="$PATH"

## load aliases
[ -f "$HOME/.aliases" ] && source "$HOME/.aliases"

## find any custom bash completions, and load them
if [ -d "$HOME/.bash_completion.d" ]; then
    for myfile in $(find "$HOME/.bash_completion.d" -type f)
    do
        source $myfile > /dev/null 2>&1
    done
fi

## iterm tab colors yay.
[ -f "$HOME/bin/tab_helper.sh" ] && source "$HOME/bin/tab_helper.sh"

## ruby environments
[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm" # Load RVM into a shell session *as a function*

## mess with the terminal prompt
export PS1='    [ \@ \033[31m\u\033[0m@\033[36m\h\033[0m \j \! ]\n\e[33m\w\e[39m> : '
export PROMPT_COMMAND='echo -ne "\033]0;\007"'


