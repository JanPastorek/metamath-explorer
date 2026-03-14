$( Test Metamath database for unit tests $)

$c |- wff ( -> ) $.
$v ph ps ch $.

wph $f wff ph $.
wps $f wff ps $.
wch $f wff ch $.

$( Axiom 1: Simplification theorem $)
ax-1 $a |- ( ph -> ( ps -> ph ) ) $.

$( Axiom 2: Distribution $)
ax-2 $a |- ( ( ph -> ( ps -> ch ) ) -> ( ( ph -> ps ) -> ( ph -> ch ) ) ) $.

${
   min $e |- ph $.
   maj $e |- ( ph -> ps ) $.
   $( Rule of Modus Ponens $)
   ax-mp $a |- ps $.
$}

$( A simple proposition proved from axioms $)
a1i.1 $e |- ps $.
a1i $p |- ( ph -> ps ) $= ( ax-1 ax-mp ) $.
