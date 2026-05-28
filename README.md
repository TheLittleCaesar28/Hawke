echo "# HAWKE - Lenguaje para Control de Brazo Robótico" > README.md
echo "" >> README.md
echo "## Descripción" >> README.md
echo "Lenguaje de programación para controlar un brazo robótico tipo pinza con capacidad de giro." >> README.md
echo "" >> README.md
echo "## Instalación" >> README.md
echo "```bash" >> README.md
echo "git clone https://github.com/TheLittleCaesar28/Hawke.git" >> README.md
echo "cd Hawke/src" >> README.md
echo "pip install pyserial" >> README.md
echo "python main.py" >> README.md
echo "```" >> README.md

git add README.md
git commit -m "Agregar README"
git push
