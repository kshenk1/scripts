#!/bin/bash

PATH="$PATH"

export CLICOLOR=0

[ -d "$HOME/bin" ] && PATH="$PATH:$HOME/bin"

[ -f "$HOME/bin/tab_helper.sh" ] && source $HOME/bin/tab_helper.sh

export PATH="$PATH"
export PS1='    [ \@ \033[31m\u\033[0m@\033[36m\h\033[0m \j \! ]\n\w> : '
export PROMPT_COMMAND='echo -ne "\033]0;\007"'

[ -f "$HOME/.aliases" ] && source $HOME/.aliases

## find any custom bash completions, and load them
if [ -d "$HOME/.bash_completion.d" ]; then
	for myfile in $(find "$HOME/.bash_completion.d" -type f)
	do
		source $myfile > /dev/null 2>&1
	done
fi

[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm" # Load RVM into a shell session *as a function*

