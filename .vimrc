" We shan't be highlighting text incorrectly nor slowly, shan't we?
syntax sync fromstart

" no automatic newline at end of file! 
setlocal binary noeol

" STFU
set noerrorbells visualbell t_vb=
autocmd GUIEnter * set visualbell t_vb=

" Wildmenu allows shell-like opening of new files.
set wildmenu
set wildmode=list:longest


" The most badass color scheme known to man
set background=dark 
colorscheme ir_black
syntax on

" This would only ever be needed in a system-wide config
"set nocompatible 

" Tabstops, indents, and other edit configs
set ruler
set showmode
"set textwidth=80
set showmatch
set ignorecase
set smartcase
set tabstop=4
set shiftwidth=4
set autoindent
set autowrite
set backspace=indent,eol,start
set incsearch
"set noexpandtab
set expandtab
set mouse=r
set t_kD=<Ctrl-v><fn-Delete>


" Key mappings "
       
" Map Alt-/ to search a visual selection FIXME
"vnoremap <M-/> <Esc>/\%V
"nnoremap <M-/> /\%V

" Fix Page*, Home, End, etc. so they are actually useful
map <silent> <PageUp> 1000<C-U>
map <silent> <PageDown> 1000<C-D>
imap <silent> <PageUp> <C-O>1000<C-U>
imap <silent> <PageDown> <C-O>1000<C-D>
map ^[[H <Home>
imap ^[[H <Home>
map ^E <End>
imap ^E <End>
imap ^D <Delete>

" Not sure what these do
map - <c-w>w
imap jj <Esc>

