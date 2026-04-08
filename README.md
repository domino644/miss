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

## 6. Porównanie z bazowym modelem pożaru lasu

Bazowy model pożaru lasu to prosty automat komórkowy, w którym każda komórka może znajdować się w jednej z kilku dyskretnych stanów, na przykład: pusta, drzewo albo płonąca. Ogień rozprzestrzenia się wyłącznie na najbliższe sąsiednie komórki zgodnie ze stałą lokalną regułą. Taki model zazwyczaj nie uwzględnia ukształtowania terenu, warunków pogodowych ani rzeczywistych danych środowiskowych. Jego głównym celem jest badanie ogólnych mechanizmów rozprzestrzeniania się pożaru, a nie odtwarzanie realnych zdarzeń pożarowych.

W przeciwieństwie do tego, zastosowany tutaj model rozwija podejście bazowe na kilka istotnych sposobów.

Po pierwsze, prawdopodobieństwo zapłonu nie jest już stałe. Zależy ono od takich czynników jak typ roślinności, gęstość roślinności, wiatr oraz topografia terenu. Dzięki temu symulacja staje się przestrzennie niejednorodna i znacznie lepiej oddaje rzeczywiste zachowanie ognia.

Po drugie, model wykorzystuje rzeczywiste dane geoprzestrzenne i meteorologiczne, między innymi dane o pokryciu terenu, nachyleniu wyznaczonym na podstawie wysokości terenu, prędkości i kierunku wiatru, drogach, ciekach wodnych oraz obszarach spalonych we wcześniejszych pożarach. W efekcie symulacja nie jest już wyłącznie abstrakcyjnym procesem na siatce, ale rekonstrukcją rozprzestrzeniania się pożaru opartą na danych dla konkretnego obszaru.

Po trzecie, model wprowadza rozszerzoną, nielokalną regułę propagacji oznaczoną jako N2, która pozwala ogniowi przemieszczać się dalej w kierunku wiatru niż w standardowym układzie najbliższych sąsiadów. Przy silnym wietrze zapłon może nastąpić kilka komórek dalej, co lepiej odwzorowuje szybkie rozprzestrzenianie się pożaru napędzanego wiatrem i częściowo oddaje efekty zbliżone do spottingu. Jest to jedna z kluczowych różnic względem modelu bazowego, w którym propagacja jest wyłącznie lokalna.

Wreszcie, zamiast generować tylko jeden abstrakcyjny przebieg symulacji, model uruchamiany jest w postaci zespołu wielu symulacji, aby oszacować prawdopodobieństwo spalenia danego obszaru oraz wzorce czasu dotarcia pożaru. Dzięki temu lepiej nadaje się do analizy rzeczywistych scenariuszy pożarowych niż klasyczny bazowy automat pożaru lasu.

Krótko mówiąc, w porównaniu z bazowym modelem pożaru lasu ta wersja dodaje niejednorodne reguły zapłonu, wpływ wiatru i terenu, rzeczywiste dane GIS i meteorologiczne, bariery takie jak drogi i cieki wodne, nielokalne rozprzestrzenianie zależne od wiatru oraz probabilistyczną symulację opartą na wielu uruchomieniach.
