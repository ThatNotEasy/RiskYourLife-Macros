# 1. Add the .gitignore rules
echo "__pycache__/
*.py[cod]" >> .gitignore

# 2. Remove already tracked cache files
git rm -r --cached modules/__pycache__/

# 3. Commit the cleanup
git add .gitignore
git commit -m "Ignore Python cache files (__pycache__)"