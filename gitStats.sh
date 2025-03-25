#!/bin/bash

# Generate the git logs and save them to a temporary file
git log --pretty=format:"commit %H%nAuthor: %an <%ae>%nDate: %ad" > git.logs.temp

# Sum of total commits
sumTotal=$(cat git.logs.temp | grep -e "commit" | wc -l)

# Sum of commits for each author
sumFilter=0

# Number of commits by Ale (rabeloguedes or Guedes)
commitsAle=$(cat git.logs.temp | grep -e "rabeloguedes" -e "Guedes" | wc -l)
sumFilter=$((sumFilter + commitsAle))

echo "Number of commits by Ale: $commitsAle"

# Number of commits by Alex (ahokcool or Alex)
commitsAlex=$(cat git.logs.temp | grep -e "ahokcool" -e "Alex" | wc -l)
sumFilter=$((sumFilter + commitsAlex))
echo "Number of commits by Alex: $commitsAlex"

# Number of commits by Anatolii (Anatolii or Ash)
commitsAnatolii=$(cat git.logs.temp | grep -e "Anatolii" -e "Ash" | wc -l)
sumFilter=$((sumFilter + commitsAnatolii))
echo "Number of commits by Anatolii: $commitsAnatolii"

# Number of commits by Finacio97 (Finacio97 or xico)
commitsFinacio97=$(cat git.logs.temp | grep -e "Finacio97" -e "xico" | wc -l)
sumFilter=$((sumFilter + commitsFinacio97))
echo "Number of commits by Finacio97: $commitsFinacio97"

# Number of commits by Rajh (Rajh or rajh)
commitsRajh=$(cat git.logs.temp | grep -e "Rajh" -e "rajh" | wc -l)
sumFilter=$((sumFilter + commitsRajh))
echo "Number of commits by Rajh: $commitsRajh"

# Number of commits by Joao (Miranda or Joao)
commitsJoao=$(cat git.logs.temp | grep -e "Miranda" -e "Joao" | wc -l)
sumFilter=$((sumFilter + commitsJoao))
echo "Number of commits by Joao: $commitsJoao"

# Error check: Compare the sum of filtered commits to the total
echo "Error check: $sumFilter / $sumTotal"

# Clean up by removing the temporary file
rm git.logs.temp
