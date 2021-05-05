# Dyson-Sphere-Program-chain-manipulation
Dyson Sphere Program production chain manipulation tool



# SUMMARY :
Script listing all the components and buildings in the game Dyson Sphere
Program.
- allows to return partial or complete production chain of any item.
- Each chain can be scaled to targeted production per second (pps).
- each displayed item in the chain will show up its required  pps and the
  number of factories needed to reach it.
- total : a listing of all item needed (merged by item) by the chain can be
  displayed
- totals fo several chains can be combined with each other
- you can get a listing of every building/components using a specific product,
  either directly, either indirectly (those that needs it in their chain of
  production)

# USAGE :

## I. Products : Creating a new component/building :
Components or Buildings are treated the same way, no difference is made

Product( *name*, *units_per_cycle* , *cycle_time* , [ *requirement_name* = *number_required*, [...] ] )

*name* : <str> name of the product
*units_per_cycle* : <int> number of units produced per cycle
*cycle_time* : <float> time spent for the cycle to complete
*requirement_name* : <str> name of the needed component/building
*number_required* : <int> number of units needed

ex :
    >>> Product("Iron_Ore", 1, 1)
    >>> Product("Iron_Ingot", 1, 1, Iron_Ore=1)
    >>> Product("Magnetic_Coil", 2, 1, Magnetic_Ring = 2, Copper_Ingot = 1)

If you want to add a product, you add these commands at the bottom of this script rather than the
console, otherwise your additions will be forgoten when you close the console

## II. Nodes :
### a. Creating a chain :
Node( name , [ production_per_second ] )

name : <str> name of the product
production_per_second : production/sec to achieve

NOTE : parameter name must be a product name that has already been created (see chapter I.)

    >>> coil = Node("Magnetic_Coil")
    when production/sec is not given, default product production/sec is used
    >>> coil = Node("Magnetic_Coil", 6)

you can change the targeted production/sec of an existing node :
    >>> coil.set_pps(2)

### b. displaying production chain :
To display the full chain :
```
>>> coil.print()
< Magnetic_Coil @ 2.00/sec (x1.00) >
    < Magnetic_Ring @ 2.00/sec (x3.00) >
        < Iron_Ore @ 2.00/sec (x2.00) >
    < Copper_Ingot @ 1.00/sec (x1.00) >
        < Copper_Ore @ 1.00/sec (x1.00) >
```

To display only the first level of the chain :
```
>>> coil.print(depth=1)
< Magnetic_Coil @ 2.00/sec (x1.00) >
    < Magnetic_Ring @ 2.00/sec (x3.00) >
    < Copper_Ingot @ 1.00/sec (x1.00) >
```

the output should be self explanatory, but let's explain it.
In the previous example, let's take this line of the output :
    < Magnetic_Coil @ 2.00/sec (x1.00) >
and now translate it :
    < product_name @(at) production/sec ( required number of factories to achieve prod/sec ) >

### c. obtaining total factories needed
Totals are the sum of factories needed in a chain, regrouped by item.
Let's take the example of the Oil_Extractor, almost all of its needed
componenets need Iron_Ingot and/or Copper_Ingot. Total will regroup all
Iron_Ingots together, same for each product.

Total are obtained from created chains, like the previously created coil.
you can get the total from a full chain like this :
```
>>> coil_total = coil.total()
```

or you can get total from a partial chain, like this:
```
>>> coil_total = coil.total(depth=1)
```

while production chains are Node Objects, totals are different objects, in the previous
usage example, coil_total is a Total object.

## III. Totals :
### a. dislaying totals :
    >>> coil_total.print()
    Copper_Ingot  x 1.0 : 1.0/sec
    Copper_Ore  x 1.0 : 1.0/sec
    Iron_Ore  x 2.0 : 2.0/sec
    Magnetic_Coil  x 1.0 : 2.0/sec
    Magnetic_Ring  x 3.0 : 2.0/sec

totals can be organized by different criterias:
- by name (default)
- by production/sec
```
>>> coil_total.print(sort_key=sort_key_pps)
Copper_Ingot  x 1.0 : 1.0/sec
Copper_Ore  x 1.0 : 1.0/sec
Magnetic_Coil  x 1.0 : 2.0/sec
Magnetic_Ring  x 3.0 : 2.0/sec
Iron_Ore  x 2.0 : 2.0/sec
```
- by number of factories
```
>>> coil_total.print(sort_key=sort_key_factory)
Magnetic_Coil  x 1.0 : 2.0/sec
Copper_Ingot  x 1.0 : 1.0/sec
Copper_Ore  x 1.0 : 1.0/sec
Iron_Ore  x 2.0 : 2.0/sec
Magnetic_Ring  x 3.0 : 2.0/sec
```

by default the order is ascending, but it can be descending :

    >>> coil_total.print( descending = True )
    >>> coil_total.print( sort_key = sort_key_factory, descending = True)

### b. combining totals :
Total objects can be combined together. The result can be achieve in several ways
first, let's create some chains :

    >>> board = Node("Circuit_Board", 6)
    >>> tesla = Node("Tesla_Tower", 6)
    >>> belts = Node("Conveyor_Belt_MKI", 6)

Now, method #1 to combine totals :

    >>> combined_total = tesla.total() + boards.total() + belts.total()

method #2

    >>> combined_total = tesla.total().sum_with(boards.total(), belts.total())

method #3

    >>> combined_total = Total.sum_nodes([tesla, boards, belts])

for method #3, if you want to combine partial chains :

    >>> combined_total = Total.sum_nodes( [tesla, boards, belts], depths=[1,2,1] )


## IV. Getting all products name requiring a specific product
You can either obtaining a <set> of product name requiring DIRECTLY a specific item

    >>> which_uses("Silicon_Ore")
    {'High_Purity_Silicon'}

Or obtaining thos that require INDIRECTLY a specific item, meaning needing it somewhere down its chain:

    >>> which_uses("Silicon_Ore", indirectly=True)
    {'Satellite_Substation', 'Fractionator', ... }

Here is an example use case : you discover a planet with every resources but copper, and you want to know
what you can produce without copper

    >>> items = all_products()
    >>> copper = which_uses("Copper_Ore", indirectly=True)
    >>> items - copper
    {'Titanium_Alloy', 'Hydrogen', 'Organic_Crystal', 'Conveyor_Belt_MKI', ... }
