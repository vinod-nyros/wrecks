grep -nrI --color --exclude-dir='.svn' --exclude-dir='old' --exclude-dir='fixtures' --exclude-dir='eracks9' \
    --exclude='*.pyc' --exclude='*~' --exclude='*.log' --exclude-dir='log' --exclude-dir='static' \
    --exclude-dir='packages' --exclude-dir='docs' --exclude='*.min.js' "$@" *
