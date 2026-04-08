# Projekt: Modelowanie i symulacja pożarów lasów

## 1. Autorzy
- Łukasz Wilański
- Jakub Ciszewski

## 2. Wstęp
Pożary lasów stanowią jedno z najpoważniejszych zagrożeń środowiskowych współczesnego świata. W ostatnich latach szczególnie dotkliwe skutki tego zjawiska obserwowane są w Ameryce Północnej, gdzie wysokie temperatury, długotrwałe susze, silny wiatr oraz działalność człowieka sprzyjają powstawaniu i rozprzestrzenianiu się ognia. Skala strat obejmuje nie tylko zniszczenie ekosystemów, lecz także ogromne koszty gospodarcze i społeczne.

Celem naszego projektu jest stworzenie uproszczonego modelu symulacyjnego pożarów lasów oraz zbadanie, czy rozkład wielkości pożarów może być opisywany przez rozkład potęgowy (*power law*). Interesuje nas również wskazanie czynników, które w największym stopniu wpływają na prawdopodobieństwo wystąpienia dużych pożarów, a także zaproponowanie działań, które mogłyby ograniczać ryzyko ich powstawania.

Więcej o tym można znaleźć w paperze - [Critical Behaviour of the Drossel-Schwabl Forest Fire Model](https://arxiv.org/abs/cond-mat/0202022).

## 3. Opis problemu
Pożary lasów są zjawiskiem złożonym, wynikającym z oddziaływania wielu czynników losowych i środowiskowych. Ogień może zostać zapoczątkowany przez naturalne źródła, takie jak pioruny, ale również przez działalność człowieka. Po rozpoczęciu pożaru jego dalszy rozwój zależy między innymi od gęstości roślinności, warunków pogodowych, ukształtowania terenu oraz obecności naturalnych barier, takich jak rzeki czy obszary pozbawione drzew.

W literaturze i analizach statystycznych często zwraca się uwagę, że wielkość pożarów nie rozkłada się równomiernie — większość pożarów jest mała, natomiast nieliczne osiągają bardzo duże rozmiary. Tego typu zachowanie może sugerować występowanie rozkładu potęgowego, który często pojawia się w układach złożonych i procesach o charakterze krytycznym.

Jako materiał wprowadzający do problemu można wykorzystać krótki film edukacyjny National Geographic:

[Wildfires 101 | National Geographic](https://www.youtube.com/watch?v=5hghT1W33cY)

oraz film Veritasium poświęcony tematyce power law:

[Power Law](https://youtu.be/HBluLfX2F_k)

## 4. Jak chcemy przeprowadzić symulację
Planujemy zamodelować las jako dwuwymiarową siatkę o rozmiarze \(n \times m\). Każda komórka mapy będzie reprezentowała fragment terenu, który może należeć do jednej z kilku kategorii, na przykład:
- drzewo,
- puste pole,
- przeszkoda terenowa (np. rzeka lub step),
- obszar już spalony.

Symulacja będzie przebiegać w krokach czasowych. W każdym kroku z pewnym prawdopodobieństwem w losową komórkę może uderzyć piorun, inicjując pożar. Następnie ogień będzie rozprzestrzeniał się na sąsiednie komórki zgodnie z ustalonymi regułami, zależnymi od parametrów modelu, takich jak:
- zagęszczenie drzew w lesie,
- prawdopodobieństwo zapłonu po uderzeniu pioruna,
- tempo rozprzestrzeniania się ognia,
- wpływ przeszkód terenowych ograniczających propagację pożaru,
- ewentualne dodatkowe warunki środowiskowe.

W kolejnych wersjach modelu chcemy rozszerzyć symulację o bardziej realistyczne elementy, takie jak zróżnicowanie terenu lub kierunkowe rozprzestrzenianie się ognia. Dla każdej konfiguracji parametrów będziemy uruchamiać wiele niezależnych symulacji, a następnie analizować rozmiary powstałych pożarów, ich częstość oraz zależność od przyjętych warunków początkowych.

Aby zwalidować wyniki, planujemy porównać dane uzyskane w symulacji ze zbiorem danych dotyczącym rzeczywistych pożarów lasów w Ameryce Północnej. Pozwoli to ocenić, czy model odtwarza najważniejsze cechy badanego zjawiska i czy obserwowany rozkład wielkości pożarów rzeczywiście przypomina rozkład potęgowy.

[National Fire Database fire polygon data](https://cwfis.cfs.nrcan.gc.ca/datamart/download/nfdbpoly)

Do przeprowadzenia symulacji możemy użyć gotowego [modelu Fire w programie NetLogo](https://ccl.northwestern.edu/netlogo/models/Fire).

## 5. Co chcemy osiągnąć
Naszym głównym celem jest sprawdzenie, czy nawet stosunkowo prosty model komórkowy potrafi odtworzyć podstawowe własności rzeczywistych pożarów lasów. W szczególności chcemy:
- zbadać, czy rozmiary pożarów w symulacji wykazują cechy rozkładu *power law*,
- określić, które parametry modelu mają największy wpływ na powstawanie dużych pożarów,
- porównać wyniki symulacji z rzeczywistymi danymi historycznymi,
- zaproponować możliwe strategie ograniczania ryzyka występowania dużych pożarów, na przykład poprzez zmianę gęstości zalesienia, tworzenie barier terenowych lub inne działania prewencyjne.

Ostatecznie projekt ma pokazać, że modelowanie i symulacja mogą być użytecznym narzędziem do analizy złożonych zjawisk przyrodniczych oraz do wspierania decyzji związanych z ochroną środowiska i zarządzaniem kryzysowym.

## 6. Rozszerzenie bazowego modelu

Chcemy rozszerzyć bazowy model o heterogeniczne środowisko, w którym prawdopodobieństwo zapłonu zależy od lokalnych cech komórki, przede wszystkim od typu roślinności i gęstości roślinności. Oprzemy to na podejściu z modelu Alexandridisa, w którym:

$p_{burn} = p_0 (1 + p_{veg}) (1 + p_{den}) p_w p_s$

gdzie $p_0$ to bazowe prawdopodobieństwo zapłonu, $p_veg$ opisuje wpływ typu roślinności, $p_den$ wpływ gęstości roślinności, $p_w$ wpływ wiatru, a $p_s$ wpływ nachylenia terenu.

W naszym modelu chcemy uwzględnić typ roślinności, gęstość roślinności, wiatr oraz obecność dróg i cieków wodnych, które mogą działać jako bariery ograniczające rozprzestrzenianie się ognia. Dodatkowo w przyszłości można rozważyć przejście ze stanów dyskretnych na stany ciągłe, gdzie stan komórki opisywałby np. stopień spalenia paliwa lub intensywność pożaru.

Korzyścią z zastosowania rozszerzonego modelu jest przede wszystkim większy realizm symulacji. W przeciwieństwie do bazowego automatu, taki model uwzględnia lokalne zróżnicowanie środowiska, na przykład typ i gęstość roślinności, wiatr, teren, drogi i cieki wodne, dzięki czemu lepiej odwzorowuje rzeczywiste warunki rozprzestrzeniania się pożaru.

Rozszerzone modele są zwykle trafniejsze od prostego modelu bazowego, ponieważ pozwalają lepiej przewidywać kierunek i tempo propagacji ognia. Jednocześnie zachowują zaletę automatów komórkowych, czyli stosunkowo niską złożoność obliczeniową i możliwość szybkiej symulacji dużych obszarów.

Ich dodatkową zaletą jest możliwość wykorzystania rzeczywistych danych geoprzestrzennych i meteorologicznych oraz generowania map prawdopodobieństwa spalenia, co zwiększa ich wartość praktyczną. Dzięki temu takie modele mogą wspierać analizę ryzyka, planowanie działań gaśniczych i ocenę obszarów najbardziej zagrożonych.

Trzeba jednak pamiętać, że nadal są to modele uproszczone. Ich celem nie jest idealne odwzorowanie całej fizyki pożaru, lecz osiągnięcie dobrego kompromisu między realizmem, trafnością i szybkością obliczeń.

Źródła:
https://www.mdpi.com/2571-6255/9/3/108
https://nhess.copernicus.org/articles/19/169/2019/


