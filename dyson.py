# Author : Nicolas DAVID
# Version : 0.2
# Contributors : Nicolas DAVID
# license : GNU GPL 3.0
# license linkk : https://www.gnu.org/licenses/gpl-3.0
# project address and manual : https://github.com/Nlight91/Dyson-Sphere-Program-chain-manipulation
import re

db = {}

def _which_uses(key, indirectly=False):
    key = format_name(key)
    if not indirectly :
        for product in db.values():
            if key in product :
                yield product.name
    elif indirectly :
        for name in db:
            tree = Chain(name)
            if key in tree.total() :
                yield name

def which_uses(key, indirectly=False):
    return set(_which_uses(key, indirectly=indirectly))

def all_products():
    return set(db.keys())

def format_name(string):
    words = re.findall("[a-zA-Z0-9]+", string)
    return "_".join(w.capitalize() for w in words)


class Product:
    def __init__(s, name, units, time, **reqs):
        name = format_name(name)
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
            key = format_name(key)
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
        key = format_name(key)
        return key in s.reqs


class Chain:
    @property
    def pps(s):
        return s.adjusted_product.pps
    @property
    def base_pps(s):
        return s.base_product.pps

    def __init__(s, name, tgt_pps=None):
        name = format_name(name)
        product = db[name]
        tgt_pps = product.pps if tgt_pps is None else tgt_pps
        s.name = name
        s.base_product = product
        s.factory_number = product.objective(tgt_pps)
        s.adjusted_product = product * s.factory_number
        s.children = []
        for key,tgt_pps in s.adjusted_product :
            s.children.append(Chain(key, tgt_pps))

    def set_pps(s, tgt=None):
        if tgt is None:
            tgt = s.base_product.pps
        s.__init__(s.name, tgt_pps = tgt)

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
        assert type(o) is Chain
        assert o.name == s.name
        return Chain(s.name, s.adjusted_product.pps + o.adjusted_product.pps)

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
        key = format_name(key)
        return s.data[key]

    def __setitem__(s, key, value):
        key = format_name(key)
        assert type(value) is Chain
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
        assert all([type(n) is Chain for n in nodes])
        if depths is None :
            totals = [node.total() for node in nodes]
        else :
            assert len(depths) == len(nodes)
            totals = [nodes[x].total(depth=depths[x]) for x in range(len(nodes))]
        dic = Total()
        return dic.sum_with(*totals)

    def  print(s, sort_key = None, descending=False):
        for name, node in sorted(s.items(), key=sort_key, reverse=descending) :
            print(f"{name}  x {node.factory_number} : {node.pps}/sec")

def sort_key_name(item):
    return item[0]

def sort_key_pps(item):
    return item[1].pps

def sort_key_factory(item):
    return item[1].factory_number

# ==== COMPONENTS ====

Product("Coal",3,1)
Product("Copper_Ore", 3,1)
Product("Crude_Oil",3,1)
Product("Iron_Ore", 3, 1)
Product("Stone",3,1)
Product("Silicon_Ore", 1, 10, Stone=10)
Product("Titanium_Ore",3,1)
Product("Water",3,1)
Product("Copper_Ingot", 1, 1, Copper_Ore = 1)
Product("Magnetic_Ring", 1, 1.5, Iron_Ore = 1)
Product("Magnetic_Coil", 2, 1, Magnetic_Ring = 2, Copper_Ingot = 1)
Product("Iron_Ingot", 1, 1, Iron_Ore=1)
Product("Circuit_Board", 2,1, Iron_Ingot=2, Copper_Ingot=1)
Product("High_Purity_Silicon", 1, 2, Silicon_Ore = 2)
Product("Microcrystalline_Component",1,2, High_Purity_Silicon=2, Copper_Ingot=1)
Product("Processor", 1, 3, Circuit_Board = 2, Microcrystalline_Component = 2)
Product("Energetic_Graphite",1,2, Coal=2)
Product("Hydrogen",1,4, Crude_Oil=2)
Product("Refined_Oil",2,4, Crude_Oil=2)
Product("Plastic",1,3, Refined_Oil=2,Energetic_Graphite=1)
Product("Crystal_Silicon",1,2, High_Purity_Silicon=1)
Product("Sulfuric_Acid",4,6, Refined_Oil=6, Stone=8, Water=4)
Product("Graphene",2,3, Energetic_Graphite=3, Sulfuric_Acid=1)
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
Product("Deuteron_Fuel_Rod", 1, 6, Titanium_Alloy=1, Deuterium=10, Super_Magnetic_Ring=1)
Product("Small_Carrier_Rocket", 1,6, Dyson_Sphere_Component=2, Deuteron_Fuel_Rod=2, Quantum_Chip=2)
Product("Photon", 1, 1)
Product("Antimatter", 2, 2, Photon=2)
Product("Annihilation_Constraint_Sphere", 1,20, Particle_Container=1, Processor=1)
Product("Antimatter_Fuel_Rod", 1, 12, Antimatter=10, Hydrogen=10, Annihilation_Constraint_Sphere=1, Titanium_Alloy=1)
Product("White_Matrix", 1, 15, Blue_Matrix=1, Red_Matrix=1, Yellow_Matrix=1, Purple_Matrix=1, Green_Matrix=1, Antimatter=1)

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
Product("Conveyor_Belt_MK1", 3,1, Iron_Ingot=2, Gear=1)
Product("Conveyor_Belt_MK2",3,1, Conveyor_Belt_MK1=3, Electromagnetic_Turbine=1)
Product("Conveyor_Belt_MK3", 3,1, Conveyor_Belt_MK2=3, Super_Magnetic_Ring=1, Graphene=1)
Product("Splitter", 1,2, Iron_Ingot=3, Gear=2, Circuit_Board=1)
Product("Storage_MK1", 1,2, Iron_Ingot=4, Stone_Brick=4)
Product("Storage_MK2", 1,4, Steel=8, Stone_Brick=8)
Product("Storage_Tank", 1,2, Iron_Ingot=8, Stone_Brick=4, High_Purity_Silicon=4)
Product("EM_Rail_Ejector", 1,6, Steel=20, Gear=20, Processor=5, Super_Magnetic_Ring=10)
Product("Planetary_Logistics_Station", 1,20, Steel=40, Titanium_Ingot=40, Processor=40, Particle_Container=20)
Product("Miniature_Particle_Collider", 1,15, Titanium_Alloy=20, Frame_Material=20, Super_Magnetic_Ring=50, Graphene=10, Processor=8)
Product("Sorter_MK1", 1,1, Iron_Ingot=1, Circuit_Board=1)
Product("Sorter_MK2", 2,1, Sorter_MK1=2, Electric_Motor=1)
Product("Sorter_MK3", 2,1, Sorter_MK2=2, Electromagnetic_Turbine=1)
Product("Mining_Machine", 1,3, Iron_Ingot=4, Circuit_Board=2, Magnetic_Coil=2, Gear=2)
Product("Water_Pump", 1,4, Iron_Ingot=8, Stone_Brick=4, Electric_Motor=4, Circuit_Board=2)
Product("Oil_Extractor", 1,8, Steel=12, Stone_Brick=12, Circuit_Board=6, Plasma_Exciter=4)
Product("Oil_Refinery", 1,6, Steel=10, Stone_Brick=10, Circuit_Board=6, Plasma_Exciter=6)
Product("Interstellar_Logistics_Station", 1,30, Planetary_Logistics_Station=1, Titanium_Alloy=40, Particle_Container=20)
Product("Assembling_Machine_MK1", 1,2, Iron_Ingot=4, Gear=8, Circuit_Board=4)
Product("Assembling_Machine_MK2", 1,3, Assembling_Machine_MK1=1, Graphene=8, Processor=4)
Product("Assembling_Machine_MK3", 1, 4, Assembling_Machine_MK2=1, Particle_Broadband=8, Quantum_Chip=2)
Product("Smelter", 1,3, Iron_Ingot=4, Stone_Brick=2, Circuit_Board=4, Magnetic_Coil=2)
Product("Fractionator", 1,3, Steel=8, Stone_Brick=4, Glass=4, Processor=1)
Product("Chemical_Plant", 1,5, Steel=8, Stone_Brick=8, Glass=8, Circuit_Board=2)
Product("Matrix_Lab", 1,3, Iron_Ingot=8, Glass=4, Circuit_Board=4, Magnetic_Coil=4)
Product("Orbital_Collector", 1,30, Interstellar_Logistics_Station=1, Super_Magnetic_Ring=50, Reinforced_Thruster=20, Accumulator_Full=20)
Product("Satellite_Substation", 1,5 , Wireless_Power_Tower=1, Super_Magnetic_Ring=10, Frame_Material=2)
Product("Vertical_Launching_Silo", 1, 30, Titanium_Alloy=80, Frame_Material=30, Graviton_Lens=20, Quantum_Chip=10)
Product("Artificial_Star", 1, 30, Titanium_Alloy=20, Frame_Material=20, Annihilation_Constraint_Sphere=10, Quantum_Chip=10)
