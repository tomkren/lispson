# lispson
Runnable code encoded in JSON inspired by lambda calculus and Lisp.

The rest is for now in czech language (I will translate or move it soon, hopefully).

## Vypsychlejší nápady pro budoucí vylomeniny
Což takhle udělat rovnou generátor dekodérů pro další jazyky s evalem?
Idea je taková, že třeba JavaScriptový kód bude velice podobný, tak proč ho psát v JavaScriptu?
Pro cílový jazyk můžeme definovat několik konstrukcí, ze kterých pak poskládáme potřebný kód dekodéru.
Pokud by se to povedlo, tak by celá věc možná šla přepsat "v lispsonu".

Asi je rozumnější než se o něco takového snažit přímo, nejprve napsat JS kód ručně co nejpodobnější tomu Pythonovému.
Pak bude líp vidět, kde jsou ty švy, podél kterých je to potřeba střihnout.

Respektive nejelegantnější plán lze nejspíš formulovat následovně:

1) Je rozdíl v kterém jazyku běží dekodér a do kterého jazyka dekodér překládá. 
   Změnit jazyk do kterého překládá je poměrně triviální.
2) Pak lze napsat kód samotného dekodéru jako program v lispsonu.
3) Ten pak stačí dekódovat (klidně pythonovým dekodérem) do JavaScriptu. A je to! :)

