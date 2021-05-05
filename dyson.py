# Author : Nicolas DAVID
# Version : 0.1
# Contributors : Nicolas DAVID
#
"""
  SUMMARY :
  =========
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

 USAGE :
 =======
    I. Products : Creating a new component/building :
    --------------------------------------
        Components or Buildings are treated the same way, no difference is made

        Product( name, units_per_cycle , cycle_time , [ requirement_name = number_required, [...] ] )

        name : <str> name of the product
        units_per_cycle : <int> number of units produced per cycle
        cycle_time : <float> time spent for the cycle to complete
        requirement_name : <str> name of the needed component/building
        number_required : <int> number of units needed

        ex :
        >>> Product("Iron_Ore", 1, 1)
        >>> Product("Iron_Ingot", 1, 1, Iron_Ore=1)
        >>> Product("Magnetic_Coil", 2, 1, Magnetic_Ring = 2, Copper_Ingot = 1)

        If you want to add a product, you add these commands at the bottom of this script rather than the
        console, otherwise your additions will be forgoten when you close the console

    II. Nodes :
    -----------
        a. Creating a chain :
        ~~~~~~~~~~~~~~~~~~~~~
            Node( name , [ production_per_second ] )

            name : <str> name of the product
            production_per_second : production/sec to achieve

            NOTE : parameter name must be a product name that has already been created (see chapter I.)

            >>> coil = Node("Magnetic_Coil")
            when production/sec is not given, default product production/sec is used
            >>> coil = Node("Magnetic_Coil", 6)

            you can change the targeted production/sec of an existing node :
            >>> coil.set_pps(2)

        b. displaying production chain :
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            To display the full chain :
            >>> coil.print()
            < Magnetic_Coil @ 2.00/sec (x1.00) >
                < Magnetic_Ring @ 2.00/sec (x3.00) >
                    < Iron_Ore @ 2.00/sec (x2.00) >
                < Copper_Ingot @ 1.00/sec (x1.00) >
                    < Copper_Ore @ 1.00/sec (x1.00) >

            To display only the first level of the chain :
            >>> coil.print(depth=1)
            < Magnetic_Coil @ 2.00/sec (x1.00) >
                < Magnetic_Ring @ 2.00/sec (x3.00) >
                < Copper_Ingot @ 1.00/sec (x1.00) >

            the output should be self explanatory, but let's explain it.
            In the previous example, let's take this line of the output :
            < Magnetic_Coil @ 2.00/sec (x1.00) >
            and now translate it :
            < product_name @(at) production/sec ( required number of factories to achieve prod/sec ) >

        c. obtaining total factories needed
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Totals are the sum of factories needed in a chain, regrouped by item.
            Let's take the example of the Oil_Extractor, almost all of its needed
            componenets need Iron_Ingot and/or Copper_Ingot. Total will regroup all
            Iron_Ingots together, same for each product.

            Total are obtained from created chains, like the previously created coil.
            you can get the total from a full chain like this :
            >>> coil_total = coil.total()

            or you can get total from a partial chain, like this:
            >>> coil_total = coil.total(depth=1)

            while production chains are Node Objects, totals are different objects, in the previous
            usage example, coil_total is a Total object.

    III. Totals :
    =============
        a. dislaying totals :
        ~~~~~~~~~~~~~~~~~~~~~
            >>> coil_total.print()
            Copper_Ingot  x 1.0 : 1.0/sec
            Copper_Ore  x 1.0 : 1.0/sec
            Iron_Ore  x 2.0 : 2.0/sec
            Magnetic_Coil  x 1.0 : 2.0/sec
            Magnetic_Ring  x 3.0 : 2.0/sec

            totals can be organized by different criterias:
            - by name (default)

            - by production/sec
            >>> coil_total.print(sort_key=sort_key_pps)
            Copper_Ingot  x 1.0 : 1.0/sec
            Copper_Ore  x 1.0 : 1.0/sec
            Magnetic_Coil  x 1.0 : 2.0/sec
            Magnetic_Ring  x 3.0 : 2.0/sec
            Iron_Ore  x 2.0 : 2.0/sec

            - by number of factories
            >>> coil_total.print(sort_key=sort_key_factory)
            Magnetic_Coil  x 1.0 : 2.0/sec
            Copper_Ingot  x 1.0 : 1.0/sec
            Copper_Ore  x 1.0 : 1.0/sec
            Iron_Ore  x 2.0 : 2.0/sec
            Magnetic_Ring  x 3.0 : 2.0/sec

            by default the order is ascending, but it can be descending :
            >>> coil_total.print( descending = True )
            >>> coil_total.print( sort_key = sort_key_factory, descending = True)

        b. combining totals :
        ~~~~~~~~~~~~~~~~~~~~~
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


    IV. Getting all products name requiring a specific product
    ==========================================================
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
"""
db = {}

def _which_uses(key, indirectly=False):
    if not indirectly :
        for product in db.values():
            if key in product :
                yield product.name
    elif indirectly :
        for name in db:
            tree = Node(name)
            if key in tree.total() :
                yield name

def which_uses(key, indirectly=False):
    return set(_which_uses(key, indirectly=indirectly))

def all_products():
    return set(db.keys())


class Product:
    def __init__(s, name, units, time, **reqs):
        s.name = name
        s.units = units
        s.time = time
        s.pps = units/time
        s.reqs = {}
        s.add_reqs(reqs)
        if name not in db:
            db[name] = s

    def add_reqs(s, reqs):
        for key,val in reqs.items():
            s.reqs[key] = val/s.time
            if key not in db:
                print(f'"{key}" not in database')

    def objective(s, pps):
        return pps / s.pps

    def __repr__(s):
        reqs = ", ".join(f"{key} : {val}/sec" for key,val in s.reqs.items())
        return f'< {s.name} @{s.pps}/sec requires {reqs} >'

    def __iter__(s):
        for key,val in s.reqs.items():
            yield key,val

    def __mul__(s,scalar):
        return Product(s.name, s.pps*scalar, 1, **{key:val*scalar for key,val in s})

    def __contains__(s, key):
        return key in s.reqs


class Node:
    @property
    def pps(s):
        return s.adjusted_product.pps
    @property
    def base_pps(s):
        return s.base_product.pps

    def __init__(s, name, tgt_pps=None, parent=None):
        product = db[name]
        tgt_pps = product.pps if tgt_pps is None else tgt_pps
        s.name = name
        s.parent = parent
        s.base_product = product
        s.factory_number = product.objective(tgt_pps)
        s.adjusted_product = product * s.factory_number
        s.children = []
        for key,tgt_pps in s.adjusted_product :
            s.children.append(Node(key, tgt_pps, parent=s))

    def set_pps(s, tgt=None):
        if tgt is None:
            tgt = s.base_product.pps
        s.__init__(s.name, tgt_pps = tgt, parent = s.parent)

    def chain(s, depth=None, lvl=0, summarized=False):
        tabs = lambda x : " "*4*x
        if summarized :
            if depth is not None and lvl > depth*1:
                return
            yield (f"{tabs(lvl)}{s}")
            yield (f"{tabs(lvl+1)}---summary---")
            for child in s.children :
                yield (f"{tabs(lvl+1)}{child}")
            yield (f"{tabs(lvl+1)}---details---")
            for child in s.children :
                for line in child.chain(depth=depth, lvl=lvl+1, summarized=summarized):
                    yield line
        elif not summarized :
            if depth is not None and lvl > depth:
                return
            yield (f"{tabs(lvl)}{s}")
            for child in s.children :
                for line in child.chain(depth=depth, lvl=lvl+1, summarized=summarized):
                    yield line

    def print(s, depth=None, lvl=0, summarized=False):
        for line in s.chain(depth=depth, lvl=lvl, summarized=summarized):
            print(line)

    def __iter__(s):
        for child in s.children :
            yield child

    def __add__(s, o):
        assert type(o) is Node
        assert o.name == s.name
        return Node(s.name, s.adjusted_product.pps + o.adjusted_product.pps)

    def __repr__(s):
        return f"< {s.name} @ {s.adjusted_product.pps:.2f}/sec (x{s.factory_number:.2f}) >"

    def total(s, dic=None, depth=None, lvl=0):
        print_res = dic is None
        if dic is None :
            dic = Total()
        if depth is not None and lvl > depth:
            return
        if s.name in dic :
            dic[s.name] += s
        else :
            dic[s.name] = s
        for child in s.children:
            child.total(dic=dic, depth=depth, lvl=lvl+1)
        if print_res :
            return dic


class Total:
    def __init__(s, **kargs):
        s.data = kargs

    def __getitem__(s,key):
        return s.data[key]

    def __setitem__(s, key, value):
        assert type(value) is Node
        s.data[key] = value

    def __contains__(s, key):
        return key in s.data

    def __add__(s, total):
        assert type(total) is Total
        return s.sum_with(total)

    def keys(s):
        return s.data.keys()

    def values(s):
        return s.data.values()

    def items(s):
        return s.data.items()

    def sum_with(s, *totals):
        assert all(type(t) is Total for t in totals)
        keys = list(s.keys())
        for t in totals :
            keys.extend(t.keys())
        totals = [s] + list(totals)
        keys = set(keys)
        dic = Total()
        for key in keys :
            for t in totals:
                if key in t :
                    if key not in dic :
                        dic[key] = t[key]
                    else :
                        dic[key] += t[key]
        return dic

    @classmethod
    def sum_nodes(cls, nodes, depths=None):
        assert all([type(n) is Node for n in nodes])
        if depths is None :
            totals = [node.total() for node in nodes]
        else :
            assert len(depths) == len(nodes)
            totals = [nodes[x].total(depth=depths[x]) for x in range(len(nodes))]
        dic = Total()
        return dic.sum_with(*totals)

    def  print(s, sort_key = None, descending=False):
        for name, node in sorted(s.items(), key=sort_key) :
            print(f"{name}  x {node.factory_number} : {node.pps}/sec")

def sort_key_name(item):
    return item[0]

def sort_key_pps(item):
    return item[1].pps

def sort_key_factory(item):
    return item[1].factory_number

# ==== COMPONENTS ====

Product("Copper_Ore", 1,1)
Product("Copper_Ingot", 1, 1, Copper_Ore = 1)
Product("Iron_Ore", 1, 1)
Product("Magnetic_Ring", 1, 1.5, Iron_Ore = 1)
Product("Magnetic_Coil", 2, 1, Magnetic_Ring = 2, Copper_Ingot = 1)
Product("Iron_Ingot", 1, 1, Iron_Ore=1)
Product("Circuit_Board", 2,1, Iron_Ingot=2, Copper_Ingot=1)
Product("Silicon_Ore", 1, 1)
Product("High_Purity_Silicon", 1, 2, Silicon_Ore = 2)
Product("Microcrystalline_Component",1,2, High_Purity_Silicon=2, Copper_Ingot=1)
Product("Processor", 1, 3, Circuit_Board = 2, Microcrystalline_Component = 2)
Product("Coal",1,1)
Product("Energetic_Graphite",1,2, Coal=2)
Product("Crude_Oil",1,1)
Product("Hydrogen",1,4, Crude_Oil=2)
Product("Refined_Oil",2,4, Crude_Oil=2)
Product("Plastic",1,3, Refined_Oil=2,Energetic_Graphite=1)
Product("Crystal_Silicon",1,2, High_Purity_Silicon=1)
Product("Water",1,1)
Product("Stone",1,1)
Product("Sulfuric_Acid",4,6, Refined_Oil=6, Stone=8, Water=4)
Product("Graphene",2,3, Energetic_Graphite=3, Sulfuric_Acid=1)
Product("Titanium_Ore",1,1)
Product("Titanium_Ingot",1,2,Titanium_Ore=2)
Product("Carbon_Nanotube",2,4, Graphene=3, Titanium_Ingot=1)
Product("Particle_Broadband", 1,8, Carbon_Nanotube=2, Crystal_Silicon=2, Plastic=1)
Product("Information_Matrix",1,10, Processor = 2, Particle_Broadband = 1)
Product("Steel", 1,3, Iron_Ingot=3)
Product("Titanium_Alloy",4,12, Titanium_Ingot=4, Steel=4, Sulfuric_Acid=8)
Product("Gear",1,1, Iron_Ingot=1)
Product("Electric_Motor", 1,2, Iron_Ingot=2, Gear=1, Magnetic_Coil=1)
Product("Electromagnetic_Turbine", 1,2, Electric_Motor=2, Magnetic_Coil=2)
Product("Super_Magnetic_Ring",1,3, Electromagnetic_Turbine=2, Magnetic_Ring=3, Energetic_Graphite=1)
Product("Stone_Brick",1,1, Stone=1)
Product("Glass",1,2, Stone=2)
Product("Titanium_Glass", 2,5, Glass=2, Titanium_Ingot=2, Water=2)
Product("Prism", 2,2, Glass=3)
Product("Diamond", 1,2, Energetic_Graphite=1)
Product("Deuterium", 5,5, Hydrogen=10)
Product("Particle_Container", 1,4, Electromagnetic_Turbine=2, Copper_Ingot=2, Graphene=2)
Product("Strange_Matter", 1,6, Iron_Ingot=2, Deuterium=10, Particle_Container=2)
Product("Graviton_Lens", 1,6, Diamond=4, Strange_Matter=1)
Product("Space_Warper", 1,10, Graviton_Lens=1)
Product("Organic_Crystal", 1,6, Plastic=2, Refined_Oil=1, Water=1)
Product("Titanium_Crystal", 1,4, Organic_Crystal=1, Titanium_Ingot=3)
Product("Blue_Matrix", 1,3, Magnetic_Coil=1, Circuit_Board=1)
Product("Red_Matrix", 1,6, Energetic_Graphite=2, Hydrogen=2)
Product("Yellow_Matrix", 1,8, Diamond=1, Titanium_Crystal=1)
Product("Purple_Matrix", 1,10, Processor=2, Particle_Broadband=1)
Product("Foundation", 1,1, Stone_Brick=3, Steel=1)
Product("Hydrogen_Fuel_Rod",1,3, Titanium_Ingot=1, Hydrogen=5)
Product("Thruster", 1,4, Steel=2, Copper_Ingot=3)
Product("Logistics_Drone", 1,4, Iron_Ingot=5, Processor=2, Thruster=2)
Product("Reinforced_Thruster", 1,6, Titanium_Alloy=5, Electromagnetic_Turbine=5)
Product("Logistics_Vessel", 1,6, Titanium_Alloy=10, Processor=10, Reinforced_Thruster=2)
Product("Photon_Combiner",1,3, Prism=2, Circuit_Board=1)
Product("Solar_Sail",2,4, Graphene=1, Photon_Combiner=1)
Product("Frame_Material", 1,6, Carbon_Nanotube=4, Titanium_Alloy=1, High_Purity_Silicon=1)
Product("Dyson_Sphere_Component", 1,8, Frame_Material=3, Solar_Sail=3, Processor=3)
Product("Plasma_Exciter", 1,2, Magnetic_Coil=4, Prism=2)
Product("Casimir_Crystal", 1,4, Titanium_Crystal=1, Graphene=2, Hydrogen=12)
Product("Plane_Filter", 1,12, Casimir_Crystal=1, Titanium_Glass=2)
Product("Quantum_Chip", 1,6, Processor=2, Plane_Filter=2)
Product("Green_Matrix", 2,24, Graviton_Lens=1, Quantum_Chip=1)


# ==== BUILDINGS ====

Product("Tesla_Tower", 1,1, Iron_Ingot=2, Magnetic_Coil=1)
Product("Wireless_Power_Tower",1,3, Tesla_Tower=1, Plasma_Exciter=3)
Product("Wind_Turbine",1,4, Iron_Ingot=6, Gear=1, Magnetic_Coil=3)
Product("Thermal_Power_Station", 1,5, Iron_Ingot=10, Stone_Brick=4, Gear=4, Magnetic_Coil=4)
Product("Solar_Panel",1,5, Copper_Ingot=6, High_Purity_Silicon=6, Circuit_Board=6)
Product("Accumulator",1,5, Iron_Ingot=6, Super_Magnetic_Ring=6, Crystal_Silicon=4)
Product("Accumulator_Full",1,1)
Product("Ray_Receiver",1,8, Steel=20, High_Purity_Silicon=20, Photon_Combiner=10, Processor=5, Super_Magnetic_Ring=20)
Product("Mini_Fusion_Power_Station",1,10, Titanium_Alloy=12, Super_Magnetic_Ring=10, Carbon_Nanotube=8, Processor=4)
Product("Energy_Exchanger", 1,15, Titanium_Alloy=40, Steel=40, Processor=40, Particle_Container=8)
Product("Conveyor_Belt_MKI", 3,1, Iron_Ingot=2, Gear=1)
Product("Conveyor_Belt_MKII",3,1, Conveyor_Belt_MKI=3, Electromagnetic_Turbine=1)
Product("Conveyor_Belt_MKIII", 3,1, Conveyor_Belt_MKII=3, Super_Magnetic_Ring=1, Graphene=1)
Product("Splitter", 1,2, Iron_Ingot=3, Gear=2, Circuit_Board=1)
Product("Storage_MKI", 1,2, Iron_Ingot=4, Stone_Brick=4)
Product("Storage_MKII", 1,4, Steel=8, Stone_Brick=8)
Product("Storage_Tank", 1,2, Iron_Ingot=8, Stone_Brick=4, High_Purity_Silicon=4)
Product("EM_Rail_Ejector", 1,6, Steel=20, Gear=20, Processor=5, Super_Magnetic_Ring=10)
Product("Planetary_Logistics_Station", 1,20, Steel=40, Titanium_Ingot=40, Processor=40, Particle_Container=20)
Product("Miniature_Particle_Collider", 1,15, Titanium_Alloy=20, Frame_Material=20, Super_Magnetic_Ring=50, Graphene=10, Processor=8)
Product("Sorter_MKI", 1,1, Iron_Ingot=1, Circuit_Board=1)
Product("Sorter_MKII", 2,1, Sorter_MKI=2, Electric_Motor=1)
Product("Sorter_MKIII", 2,1, Sorter_MKII=2, Electromagnetic_Turbine=1)
Product("Mining_Machine", 1,3, Iron_Ingot=4, Circuit_Board=2, Magnetic_Coil=2, Gear=2)
Product("Water_Pump", 1,4, Iron_Ingot=8, Stone_Brick=4, Electric_Motor=4, Circuit_Board=2)
Product("Oil_Extractor", 1,8, Steel=12, Stone_Brick=12, Circuit_Board=6, Plasma_Exciter=4)
Product("Oil_Refinery", 1,6, Steel=10, Stone_Brick=10, Circuit_Board=6, Plasma_Exciter=6)
Product("Interstellar_Logistics_Station", 1,30, Planetary_Logistics_Station=1, Titanium_Alloy=40, Particle_Container=20)
Product("Assembling_Machine_MKI", 1,2, Iron_Ingot=4, Gear=8, Circuit_Board=4)
Product("Assembling_Machine_MKII", 1,3, Assembling_Machine_MKI=1, Graphene=8, Processor=4)
Product("Smeleter", 1,3, Iron_Ingot=4, Stone_Brick=2, Circuit_Board=4, Magnetic_Coil=2)
Product("Fractionator", 1,3, Steel=8, Stone_Brick=4, Glass=4, Processor=1)
Product("Chemical_Plant", 1,5, Steel=8, Stone_Brick=8, Glass=8, Circuit_Board=2)
Product("Matrix_Lab", 1,3, Iron_Ingot=8, Glass=4, Circuit_Board=4, Magnetic_Coil=4)
Product("Orbital_Collector", 1,30, Interstellar_Logistics_Station=1, Super_Magnetic_Ring=50, Reinforced_Thruster=20, Accumulator_Full=20)
Product("Satellite_Substation", 1,5 , Wireless_Power_Tower=1, Super_Magnetic_Ring=10, Frame_Material=2)
