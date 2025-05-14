# Wget
wget \
  --recursive \
  --level=1 \
  --page-requisites \
  --no-parent \
  --adjust-extension \
  --directory-prefix=home \
  --domains=welovepets.care \
  --no-host-directories \
  --convert-links \
  --execute robots=off \
  --input-file=urls.txt

# Rename files to strip ?ver=... etc.
find . -type f -name "*\?*" | while read -r file; do
  newname=$(echo "$file" | sed 's/\?.*//')
  mv "$file" "$newname"
done

find . -type f -name "*.html" -exec sed -i '' -E $'s/(href|src)=([\"\047][^\"\047]*)%3Fver=[^\"\047]*/\\1=\\2/g' {} +

find . -type f -name "*.html" -exec sed -i '' -E $'s/(href|src)=([\"\047])wp-content/\\1=\\2\\/wp-content/g' {} +

python3 -m http.server 8000 --directory home