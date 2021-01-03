import solid as sl
import numpy as np
from numpy import pi
import os.path as path


def deg2rad(degrees: float) -> float:
    return degrees * pi / 180


def rad2deg(rad: float) -> float:
    return rad * 180 / pi


# ######################
# ## Shape parameters ##
# ######################


nrows = 4  # key rows
ncols = 5  # key columns
extrarow = False

alpha = pi / 12.0  # curvature of the columns
beta = pi / 36.0  # curvature of the rows
centerrow = nrows - 3  # controls front_back tilt
centercol = 3  # controls left_right tilt / tenting (higher number is more tenting)
tenting_angle = pi / 12.0  # or, change this for more precise tenting control


if nrows > 5:
    column_style = "orthographic"
else:
    column_style = "standard"  # options include :standard, :orthographic, and :fixed

# column_style='fixed'


def column_offset(column: int) -> list:
    if column == 2:
        return [0, 2.82, -4.5]
    elif column >= 4:
        return [0, -12, 5.64]  # original [0 -5.8 5.64]
    else:
        return [0, 0, 0]


thumb_offsets = [6, -12, 7]
keyboard_z_offset = (
    9  # controls overall height# original=9 with centercol=3# use 16 for centercol=2
)

extra_width = .1  # extra space between the base of keys# original= 2
extra_height = 0.2  # original= 0.5

wall_z_offset = -5  # length of the first downward_sloping part of the wall (negative)
wall_xy_offset = 5  # offset in the x and/or y direction for the first downward_sloping part of the wall (negative)
wall_thickness = 5  # wall thickness parameter# originally 5

## Settings for column_style == :fixed
## The defaults roughly match Maltron settings
##   http://patentimages.storage.googleapis.com/EP0219944A2/imgf0002.png
## fixed_z overrides the z portion of the column ofsets above.
## NOTE: THIS DOESN'T WORK QUITE LIKE I'D HOPED.
fixed_angles = [deg2rad(10), deg2rad(10), 0, 0, 0, deg2rad(-15), deg2rad(-15)]
fixed_x = [-41.5, -22.5, 0, 20.3, 41.4, 65.5, 89.6]  # relative to the middle finger
fixed_z = [12.1, 8.3, 0, 5, 10.7, 14.5, 17.5]
fixed_tenting = deg2rad(0)

#######################
## General variables ##
#######################

lastrow = nrows - 1
cornerrow = lastrow - 1
lastcol = ncols - 1

#################
## Switch Hole ##
#################

keyswitch_height = 14.2  ## Was 14.1, then 14.25
keyswitch_width = 14.2

sa_profile_key_height = 12.7

plate_thickness = 4
mount_border = 4
mount_width = keyswitch_width + mount_border
mount_height = keyswitch_height + mount_border

plate_file = None
plate_offset = 0.0
# plate_file = path.join("..", "src", r"hot_swap_plate.stl")
# plate_offset = plate_thickness - 5.25

def single_plate(cylinder_segments=100):
    top_wall = sl.cube([keyswitch_width + mount_border, mount_border/2, plate_thickness], center=True)
    top_wall = sl.translate(
        (0, (mount_border/2 / 2) + (keyswitch_height / 2), plate_thickness / 2)
    )(top_wall)

    left_wall = sl.cube([mount_border/2, keyswitch_height + mount_border, plate_thickness], center=True)
    left_wall = sl.translate(
        ((mount_border/2 / 2) + (keyswitch_width / 2), 0, plate_thickness / 2)
    )(left_wall)
    
    holder_height = 4
    holder_post_height = 8
    holder_post_width = 2
    holder_nub_width = 0.6
    holder_nub_z = 2
    holder_slot_z = 2

    holder = sl.cube([holder_post_width, holder_post_height, plate_thickness/2 + holder_slot_z + holder_nub_z], center=True)
    holder = sl.translate(
        (mount_width/2+holder_post_width/2, 0, -(plate_thickness/2 + holder_slot_z + holder_nub_z)/2+plate_thickness/2), 
    )(holder)
    holder = sl.rotate(rad2deg(pi / 2), [0, 0, 1])(holder)
    holder2 = sl.cube([holder_post_width+holder_nub_width, holder_height, holder_nub_z], center=True)
    holder2 = sl.translate(
        (mount_width/2-(holder_nub_width-holder_post_width)/2, 0, -holder_nub_z/2-holder_slot_z)
    )(holder2)
    holder2 = sl.rotate(rad2deg(pi / 2), [0, 0, 1])(holder2)
    
    side_nub = sl.cylinder(1, 2.75, segments=cylinder_segments, center=True)
    side_nub = sl.rotate(rad2deg(pi / 2), [1, 0, 0])(side_nub)
    side_nub = sl.translate((keyswitch_width / 2, 0, 1))(side_nub)
    nub_cube = sl.cube([1.5, 2.75, plate_thickness], center=True)
    nub_cube = sl.translate(
        ((1.5 / 2) + (keyswitch_width / 2), 0, plate_thickness / 2)
    )(nub_cube)

    side_nub = sl.hull()(side_nub, nub_cube)

    plate_half1 = top_wall + left_wall + holder + holder2 #+ side_nub
    plate_half2 = plate_half1
    plate_half2 = sl.mirror([0, 1, 0])(plate_half2)
    plate_half2 = sl.mirror([1, 0, 0])(plate_half2)

    plate = plate_half1 + plate_half2

    if plate_file is not None:
        socket = sl.import_(plate_file)
        socket = sl.translate([0, 0, plate_offset])(socket)

        plate = sl.union()(plate, socket)

    return plate


################
## SA Keycaps ##
################

sa_length = 18.25
sa_double_length = 37.5


def sa_cap(Usize=1):
    # MODIFIED TO NOT HAVE THE ROTATION.  NEEDS ROTATION DURING ASSEMBLY
    sa_length = 18.25

    bw2 = Usize * sa_length / 2
    bl2 = sa_length / 2
    m = 0
    pw2 = 6 * Usize + 1
    pl2 = 6

    if Usize == 1:
        m = 17 / 2

    k1 = sl.polygon([[bw2, bl2], [bw2, -bl2], [-bw2, -bl2], [-bw2, bl2]])
    k1 = sl.linear_extrude(height=0.1, twist=0, convexity=0, center=True)(k1)
    k1 = sl.translate([0, 0, 0.05])(k1)
    k2 = sl.polygon([[pw2, pl2], [pw2, -pl2], [-pw2, -pl2], [-pw2, pl2]])
    k2 = sl.linear_extrude(height=0.1, twist=0, convexity=0, center=True)(k2)
    k2 = sl.translate([0, 0, 12.0])(k2)
    if m > 0:
        m1 = sl.polygon([[m, m], [m, -m], [-m, -m], [-m, m]])
        m1 = sl.linear_extrude(height=0.1, twist=0, convexity=0, center=True)(m1)
        m1 = sl.translate([0, 0, 6.0])(m1)
        key_cap = sl.hull()(k1, k2, m1)
    else:
        key_cap = sl.hull()(k1, k2)

    key_cap = sl.translate([0, 0, 5 + plate_thickness])(key_cap)
    key_cap = sl.color([220 / 255, 163 / 255, 163 / 255, 1])(key_cap)

    return key_cap


#########################
## Placement Functions ##
#########################


def rotate_around_x(position, angle):
    # print((position, angle))
    t_matrix = np.array(
        [
            [1, 0, 0],
            [0, np.cos(angle), -np.sin(angle)],
            [0, np.sin(angle), np.cos(angle)],
        ]
    )
    return np.matmul(t_matrix, position)


def rotate_around_y(position, angle):
    # print((position, angle))
    t_matrix = np.array(
        [
            [np.cos(angle), 0, np.sin(angle)],
            [0, 1, 0],
            [-np.sin(angle), 0, np.cos(angle)],
        ]
    )
    return np.matmul(t_matrix, position)


cap_top_height = plate_thickness + sa_profile_key_height
row_radius = ((mount_height + extra_height) / 2) / (np.sin(alpha / 2)) + cap_top_height
column_radius = (
    ((mount_width + extra_width) / 2) / (np.sin(beta / 2))
) + cap_top_height
column_x_delta = -1 - column_radius * np.sin(beta)
column_base_angle = beta * (centercol - 2)


def apply_key_geometry(
    shape,
    translate_fn,
    rotate_x_fn,
    rotate_y_fn,
    column,
    row,
    column_style=column_style,
):
    column_angle = beta * (centercol - column)

    if column_style == "orthographic":
        column_z_delta = column_radius * (1 - np.cos(column_angle))
        shape = translate_fn(shape, [0, 0, -row_radius])
        shape = rotate_x_fn(shape, alpha * (centerrow - row))
        shape = translate_fn(shape, [0, 0, row_radius])
        shape = rotate_y_fn(shape, column_angle)
        shape = translate_fn(
            shape, [-(column - centercol) * column_x_delta, 0, column_z_delta]
        )
        shape = translate_fn(shape, column_offset(column))

    elif column_style == "fixed":
        shape = rotate_y_fn(shape, fixed_angles[column])
        shape = translate_fn(shape, [fixed_x[column], 0, fixed_z[column]])
        shape = translate_fn(shape, [0, 0, -(row_radius + fixed_z[column])])
        shape = rotate_x_fn(shape, alpha * (centerrow - row))
        shape = translate_fn(shape, [0, 0, row_radius + fixed_z[column]])
        shape = rotate_y_fn(shape, fixed_tenting)
        shape = translate_fn(shape, [0, column_offset(column)[1], 0])

    else:
        shape = translate_fn(shape, [0, 0, -row_radius])
        shape = rotate_x_fn(shape, alpha * (centerrow - row))
        shape = translate_fn(shape, [0, 0, row_radius])
        shape = translate_fn(shape, [0, 0, -column_radius])
        shape = rotate_y_fn(shape, column_angle)
        shape = translate_fn(shape, [0, 0, column_radius])
        shape = translate_fn(shape, column_offset(column))

    shape = rotate_y_fn(shape, tenting_angle)
    shape = translate_fn(shape, [0, 0, keyboard_z_offset])

    return shape


def translate(shape, xyz):
    return sl.translate(xyz)(shape)


def x_rot(shape, angle):
    return sl.rotate(rad2deg(angle), [1, 0, 0])(shape)


def y_rot(shape, angle):
    return sl.rotate(rad2deg(angle), [0, 1, 0])(shape)


def key_place(shape, column, row):
    return apply_key_geometry(shape, translate, x_rot, y_rot, column, row)


def add_translate(shape, xyz):
    vals = []
    for i in range(len(shape)):
        vals.append(shape[i] + xyz[i])
    return vals


def key_position(position, column, row):
    return apply_key_geometry(
        position, add_translate, rotate_around_x, rotate_around_y, column, row
    )


def key_holes():
    hole = single_plate()
    holes = []
    for column in range(ncols):
        for row in range(nrows):
            if (column in [2, 3]) or (not row == lastrow):
                holes.append(key_place(hole, column, row))

    return sl.union()(*holes)

def z_key_holes(column):
    hole = single_plate()
    holes = []
    for row in range(nrows):
        if (extrarow and column in [2, 3]) or (not row == lastrow):
            holes.append(key_place(hole, column, row))

    return sl.union()(*holes)


def caps():
    caps = []
    for column in range(ncols):
        for row in range(nrows):
            if (column in [2, 3]) or (not row == lastrow):
                caps.append(key_place(sa_cap(), column, row))

    return sl.union()(*caps)


####################
## Web Connectors ##
####################

web_thickness = 3.5
post_size = 0.1


def web_post():
    post = sl.cube([post_size, post_size, web_thickness], center=True)
    post = sl.translate([0, 0, plate_thickness - (web_thickness / 2)])(post)
    return post


post_adj = post_size / 2


def web_post_tr():
    return sl.translate(
        [(mount_width / 2) - post_adj, (mount_height / 2) - post_adj, 0]
    )(web_post())


def web_post_tl():
    return sl.translate(
        [-(mount_width / 2) + post_adj, (mount_height / 2) - post_adj, 0]
    )(web_post())


def web_post_bl():
    return sl.translate(
        [-(mount_width / 2) + post_adj, -(mount_height / 2) + post_adj, 0]
    )(web_post())


def web_post_br():
    return sl.translate(
        [(mount_width / 2) - post_adj, -(mount_height / 2) + post_adj, 0]
    )(web_post())


def triangle_hulls(shapes):
    hulls = []
    for i in range(len(shapes) - 2):
        hulls.append(sl.hull()(*shapes[i : (i + 3)]))

    return sl.union()(*hulls)


def connectors():
    hulls = []
    for column in range(ncols - 1):
        for row in range(lastrow):  # need to consider last_row?
            # for row in range(nrows):  # need to consider last_row?
            places = []
            places.append(key_place(web_post_tl(), column + 1, row))
            places.append(key_place(web_post_tr(), column, row))
            places.append(key_place(web_post_bl(), column + 1, row))
            places.append(key_place(web_post_br(), column, row))
            hulls.append(triangle_hulls(places))

    for column in range(ncols):
        # for row in range(nrows-1):
        for row in range(cornerrow):
            places = []
            places.append(key_place(web_post_bl(), column, row))
            places.append(key_place(web_post_br(), column, row))
            places.append(key_place(web_post_tl(), column, row + 1))
            places.append(key_place(web_post_tr(), column, row + 1))
            hulls.append(triangle_hulls(places))

    for column in range(ncols - 1):
        # for row in range(nrows-1):  # need to consider last_row?
        for row in range(cornerrow):  # need to consider last_row?
            places = []
            places.append(key_place(web_post_br(), column, row))
            places.append(key_place(web_post_tr(), column, row + 1))
            places.append(key_place(web_post_bl(), column + 1, row))
            places.append(key_place(web_post_tl(), column + 1, row + 1))
            hulls.append(triangle_hulls(places))

    return sl.union()(*hulls)

def z_connectors(column):
    hulls = []
    # if column < ncols-1:
    #     for row in range(lastrow):  # need to consider last_row?
    #         # for row in range(nrows):  # need to consider last_row?
    #         places = []
    #         places.append(key_place(web_post_tl(), column + 1, row))
    #         places.append(key_place(web_post_tr(), column, row))
    #         places.append(key_place(web_post_bl(), column + 1, row))
    #         places.append(key_place(web_post_br(), column, row))
    #         hulls.append(triangle_hulls(places))

    for row in range(cornerrow):
        places = []
        places.append(key_place(web_post_bl(), column, row))
        places.append(key_place(web_post_br(), column, row))
        places.append(key_place(web_post_tl(), column, row + 1))
        places.append(key_place(web_post_tr(), column, row + 1))
        hulls.append(triangle_hulls(places))

    # if column < ncols-1:
    #     # for row in range(nrows-1):  # need to consider last_row?
    #     for row in range(cornerrow):  # need to consider last_row?
    #         places = []
    #         places.append(key_place(web_post_br(), column, row))
    #         places.append(key_place(web_post_tr(), column, row + 1))
    #         places.append(key_place(web_post_bl(), column + 1, row))
    #         places.append(key_place(web_post_tl(), column + 1, row + 1))
    #         hulls.append(triangle_hulls(places))

    return sl.union()(*hulls)

############
## Thumbs ##
############


def thumborigin():
    origin = key_position([mount_width / 2, -(mount_height / 2), 0], 1, cornerrow)
    for i in range(len(origin)):
        origin[i] = origin[i] + thumb_offsets[i]
    return origin


def thumb_tr_place(shape):
    shape = sl.rotate(10, [1, 0, 0])(shape)
    shape = sl.rotate(-23, [0, 1, 0])(shape)
    shape = sl.rotate(10, [0, 0, 1])(shape)
    shape = sl.translate(thumborigin())(shape)
    shape = sl.translate([-12, -16, 3])(shape)
    return shape


def thumb_tl_place(shape):
    shape = sl.rotate(10, [1, 0, 0])(shape)
    shape = sl.rotate(-23, [0, 1, 0])(shape)
    shape = sl.rotate(10, [0, 0, 1])(shape)
    shape = sl.translate(thumborigin())(shape)
    shape = sl.translate([-33, -15, -2])(shape)
    return shape


def thumb_mr_place(shape):
    shape = sl.rotate(-6, [1, 0, 0])(shape)
    shape = sl.rotate(-34, [0, 1, 0])(shape)
    shape = sl.rotate(48, [0, 0, 1])(shape)
    shape = sl.translate(thumborigin())(shape)
    shape = sl.translate([-29, -40, -13])(shape)
    return shape


def thumb_ml_place(shape):
    shape = sl.rotate(6, [1, 0, 0])(shape)
    shape = sl.rotate(-34, [0, 1, 0])(shape)
    shape = sl.rotate(40, [0, 0, 1])(shape)
    shape = sl.translate(thumborigin())(shape)
    shape = sl.translate([-51, -25, -12])(shape)
    return shape


def thumb_br_place(shape):
    shape = sl.rotate(-16, [1, 0, 0])(shape)
    shape = sl.rotate(-33, [0, 1, 0])(shape)
    shape = sl.rotate(54, [0, 0, 1])(shape)
    shape = sl.translate(thumborigin())(shape)
    shape = sl.translate([-37.8, -55.3, -25.3])(shape)
    return shape


def thumb_bl_place(shape):
    shape = sl.rotate(-4, [1, 0, 0])(shape)
    shape = sl.rotate(-35, [0, 1, 0])(shape)
    shape = sl.rotate(52, [0, 0, 1])(shape)
    shape = sl.translate(thumborigin())(shape)
    shape = sl.translate([-56.3, -43.3, -23.5])(shape)
    return shape


def thumb_1x_layout(shape):
    return sl.union()(
        thumb_ml_place(shape)
    )


def thumb_15x_layout(shape):
    return sl.union()(thumb_tr_place(shape), thumb_tl_place(shape),)


def double_plate():
    plate_height = (sa_double_length - mount_height) / 3
    # plate_height = (2*sa_length-mount_height) / 3
    top_plate = sl.cube([mount_width, plate_height, web_thickness], center=True)
    top_plate = sl.translate(
        [0, (plate_height + mount_height) / 2, plate_thickness - (web_thickness / 2)]
    )(top_plate)
    return sl.union()(top_plate, sl.mirror([0, 1, 0])(top_plate))


def thumbcaps():
    t1 = thumb_1x_layout(sa_cap(1))
    t15 = thumb_15x_layout(sl.rotate(pi / 2, [0, 0, 1])(sa_cap(1.5)))
    return t1 + t15


def thumb():
    plate = sl.rotate(rad2deg(pi/2), [0, 0, 1])(single_plate())
    shape = thumb_1x_layout(plate)
    shape += thumb_15x_layout(plate)
    # shape += thumb_15x_layout(double_plate())
    return shape


def thumb_post_tr():
    return sl.translate(
        [(mount_width / 2) - post_adj, (mount_height / 1.15) - post_adj, 0]
    )(web_post())


def thumb_post_tl():
    return sl.translate(
        [-(mount_width / 2) + post_adj, (mount_height / 1.15) - post_adj, 0]
    )(web_post())


def thumb_post_bl():
    return sl.translate(
        [-(mount_width / 2) + post_adj, -(mount_height / 1.15) + post_adj, 0]
    )(web_post())


def thumb_post_br():
    return sl.translate(
        [(mount_width / 2) - post_adj, -(mount_height / 1.15) + post_adj, 0]
    )(web_post())


def thumb_connectors(connect_to_main = True):
    hulls = []

    # Top two
    hulls.append(
        triangle_hulls(
            [
                thumb_tr_place(web_post_tr()),
                thumb_tl_place(web_post_tr()),
                thumb_tr_place(web_post_tl()),
                thumb_tl_place(web_post_br()),
                thumb_tr_place(web_post_tl()),
                thumb_tr_place(web_post_bl()),
                thumb_tl_place(web_post_br()),
                thumb_tl_place(web_post_bl()),
                thumb_ml_place(web_post_br()),
                thumb_tr_place(web_post_bl()),
                thumb_ml_place(web_post_bl()),
            ]
        )
    )

    # top two to the main keyboard, starting on the left
    hulls.append(
        triangle_hulls(
            [
                thumb_tl_place(web_post_tl()),
                thumb_ml_place(web_post_tr()),
                thumb_tl_place(web_post_bl()),
                thumb_ml_place(web_post_br()),
                thumb_ml_place(web_post_bl()),
            ]
        )
    )

    if connect_to_main:
        hulls.append(
            triangle_hulls(
                [
                    thumb_tl_place(web_post_tl()),
                    key_place(web_post_bl(), 0, cornerrow),
                    thumb_tl_place(web_post_tr()),
                    key_place(web_post_br(), 0, cornerrow),
                    thumb_tr_place(web_post_tl()),
                    key_place(web_post_bl(), 1, cornerrow),
                    thumb_tr_place(web_post_tr()),
                    key_place(web_post_br(), 1, cornerrow),
                    key_place(web_post_bl(), 2, lastrow),
                    thumb_tr_place(web_post_tr()),
                    key_place(web_post_bl(), 2, lastrow),
                    thumb_tr_place(web_post_br()),
                    key_place(web_post_br(), 2, lastrow),
                    key_place(web_post_bl(), 3, lastrow)
                ]
            )
        )

    return sl.union()(*hulls)


def thumb_connectors2():
    hulls = []

    hulls.append(
        triangle_hulls(
            [

                key_place(web_post_br(), 2, lastrow),
                key_place(web_post_bl(), 3, lastrow),
                key_place(web_post_tr(), 2, lastrow),
                key_place(web_post_tl(), 3, lastrow),
                key_place(web_post_bl(), 3, cornerrow),
                key_place(web_post_tr(), 3, lastrow),
                key_place(web_post_br(), 3, cornerrow),
                key_place(web_post_bl(), 4, cornerrow),
            ]
        )
    )

    hulls.append(
        triangle_hulls(
            [
                key_place(web_post_br(), 1, cornerrow),
                key_place(web_post_tl(), 2, lastrow),
                key_place(web_post_bl(), 2, cornerrow),
                key_place(web_post_tr(), 2, lastrow),
                key_place(web_post_br(), 2, cornerrow),
                key_place(web_post_bl(), 3, cornerrow),
            ]
        )
    )

    hulls.append(
        triangle_hulls(
            [
                key_place(web_post_tr(), 3, lastrow),
                key_place(web_post_br(), 3, lastrow),
                key_place(web_post_tr(), 3, lastrow),
                key_place(web_post_bl(), 4, cornerrow),
            ]
        )
    )

    return sl.union()(*hulls)

def z_thumb_connectors2(column):
    hulls = []

    if extrarow and column == 3:
        hulls.append(
            triangle_hulls(
                [
                    # key_place(web_post_br(), 2, lastrow),
                    # key_place(web_post_bl(), 3, lastrow),
                    # key_place(web_post_tr(), 2, lastrow),
                    key_place(web_post_tl(), 3, lastrow),
                    key_place(web_post_bl(), 3, cornerrow),
                    key_place(web_post_tr(), 3, lastrow),
                    key_place(web_post_br(), 3, cornerrow),
                    # key_place(web_post_bl(), 4, cornerrow),
                ]
            )
        )

    if extrarow and column == 2:
        hulls.append(
            triangle_hulls(
                [
                    # key_place(web_post_br(), 1, cornerrow),
                    key_place(web_post_tl(), 2, lastrow),
                    key_place(web_post_bl(), 2, cornerrow),
                    key_place(web_post_tr(), 2, lastrow),
                    key_place(web_post_br(), 2, cornerrow),
                    # key_place(web_post_bl(), 3, cornerrow),
                ]
            )
        )

    # hulls.append(
        # triangle_hulls(
        #     [
        #         key_place(web_post_tr(), 3, lastrow),
        #         key_place(web_post_br(), 3, lastrow),
        #         key_place(web_post_tr(), 3, lastrow),
        #         key_place(web_post_bl(), 4, cornerrow),
        #     ]
        # )
    # )

    return sl.union()(*hulls)

##########
## Case ##
##########


def bottom_hull(p, height=0.001):
    shape = None
    for item in p:
        proj = sl.projection()(p)
        t_shape = sl.linear_extrude(height=height, twist=0, convexity=0, center=True)(
            proj
        )
        t_shape = sl.translate([0, 0, height / 2 - 10])(t_shape)
        if shape is None:
            shape = t_shape
        shape = sl.hull()(p, shape, t_shape)
    return shape


left_wall_x_offset = 10
left_wall_z_offset = 3


def left_key_position(row, direction):
    pos = np.array(
        key_position([-mount_width * 0.5, direction * mount_height * 0.5, 0], 0, row)
    )
    return list(pos - np.array([left_wall_x_offset, 0, left_wall_z_offset]))


def left_key_place(shape, row, direction):
    pos = left_key_position(row, direction)
    return sl.translate(pos)(shape)


def wall_locate1(dx, dy):
    return [dx * wall_thickness, dy * wall_thickness, -1]


def wall_locate2(dx, dy):
    return [dx * wall_xy_offset, dy * wall_xy_offset, wall_z_offset]


def wall_locate3(dx, dy):
    return [
        dx * (wall_xy_offset + wall_thickness),
        dy * (wall_xy_offset + wall_thickness),
        wall_z_offset,
    ]

def connector_shape(mirror = False, offset = False, c_width = 16, c_blendWidth = 4, horizontal = False):
    c_thickness = 1.6
    c_height = 8
    c_braceWidth = 3    
    c_holeDiameter = 2.4
    c_holeToBorder = 3

    slot_length = c_width-c_holeToBorder*2+c_holeDiameter

    s = sl.translate([0, -c_blendWidth/2, 0])(sl.cube([c_thickness,c_width+c_blendWidth,c_height], center = True))
    s += sl.translate([-c_thickness/2, -c_blendWidth/2, -(c_height-c_thickness)/2])(sl.cube([c_braceWidth, c_width+c_blendWidth, c_thickness], center = True))
    s += sl.translate([-c_thickness/2, -c_blendWidth/2, (c_height-c_thickness)/2])(sl.cube([c_braceWidth, c_width+c_blendWidth, c_thickness], center = True))

    s -= sl.translate([0, c_width/2-c_holeToBorder])(
        sl.rotate(rad2deg(pi/2), [0, 1, 0])(sl.cylinder(c_holeDiameter/2, c_thickness*4, segments = 20, center = True))
    )
    if not horizontal:
        s -= sl.translate([0, c_width/2-c_holeToBorder])(
            sl.translate([0,-(slot_length)/2, 0])(sl.cube(
                [c_thickness*4, slot_length, c_holeDiameter], 
                center = True))
        )

    if horizontal:
        s = sl.rotate(rad2deg(pi/2), [0, 1, 0])(s)

    if mirror:
        if horizontal:
            s = sl.rotate(rad2deg(pi), [1, 0, 0])(s)
            s = sl.translate([0, 0, -c_thickness])(s)
        else:
            s = sl.mirror([-1, 0, 0])(s)
    s = sl.translate([c_thickness/2, c_width/2, c_height/2])(s)

    if offset:
        s = sl.translate([0, 0, c_height-c_holeDiameter])(s)

    return s

def wall_brace(place1, dx1, dy1, post1, place2, dx2, dy2, post2, skip_top = False, pos1 = None, pos2 = None, isEven = False):
    hulls = []

    if not(skip_top):
        hulls.append(place1(post1))
        hulls.append(place1(sl.translate(wall_locate2(dx1, dy1))(post1)))
        hulls.append(place1(sl.translate(wall_locate1(dx1, dy1))(post1)))
        hulls.append(place1(sl.translate(wall_locate3(dx1, dy1))(post1)))

        hulls.append(place2(post2))
        hulls.append(place2(sl.translate(wall_locate1(dx2, dy2))(post2)))
        hulls.append(place2(sl.translate(wall_locate2(dx2, dy2))(post2)))
        hulls.append(place2(sl.translate(wall_locate3(dx2, dy2))(post2)))

    shape1 = sl.hull()(*hulls)

    hulls = []
    hulls.append(place1(sl.translate(wall_locate2(dx1, dy1))(post1)))
    hulls.append(place1(sl.translate(wall_locate3(dx1, dy1))(post1)))
    hulls.append(place2(sl.translate(wall_locate2(dx2, dy2))(post2)))
    hulls.append(place2(sl.translate(wall_locate3(dx2, dy2))(post2)))
    shape2 = bottom_hull(hulls)

    result = shape1 + shape2

    if pos1:
        connector_pos = pos1(add_translate([mount_width/2, dy1*mount_height/2, 0], wall_locate3(dx1, dy1)))
        connector_pos[2] = 0
        c_shape = connector_shape(True, isEven)
        if dy1<0:
            c_shape = sl.mirror([0, -1, 0])(c_shape)
        result += sl.translate(connector_pos)(c_shape)

    if pos2:
        connector_pos = pos2(add_translate([mount_width/2, dy2*mount_height/2, 0], wall_locate3(dx2, dy2)))
        connector_pos[2] = 0
        c_shape = connector_shape(False, not(isEven))
        if dy2<0:
            c_shape = sl.mirror([0, -1, 0])(c_shape)
        result += sl.translate(connector_pos)(c_shape)

    return result

def z_thumb_connector(dx1, dy1, pos, reverse = False):
    connector_pos1 = pos(add_translate([-mount_width/2, dy1*mount_height/2, 0], wall_locate3(dx1, dy1)))
    connector_pos2 = pos(add_translate([mount_width/2, dy1*mount_height/2, 0], wall_locate3(dx1, dy1)))
    connector_pos = [(connector_pos1[0]+connector_pos2[0])/2, (connector_pos1[1]+connector_pos2[1])/2, 0]
    c_shape = connector_shape(
        c_width=6,
        c_blendWidth=12 if reverse else 4,
        horizontal=True,
        mirror=reverse)
    if dy1<0:
        c_shape = sl.mirror([0, -1, 0])(c_shape)

    return sl.translate(connector_pos)(c_shape)

def key_wall_brace(x1, y1, dx1, dy1, post1, x2, y2, dx2, dy2, post2, skip_top = False, add_connector = False):
    pos1 = None
    pos2 = None
    if add_connector:
        pos1 = (lambda pos: key_position(pos, x1, y1))
        pos2 = (lambda pos: key_position(pos, x2, y2))
    return wall_brace(
        (lambda shape: key_place(shape, x1, y1)),
        dx1,
        dy1,
        post1,
        (lambda shape: key_place(shape, x2, y2)),
        dx2,
        dy2,
        post2,
        skip_top,
        pos1,
        pos2,
        x1%2 == 0
    )


def back_wall():
    x = 0
    shape = key_wall_brace(x, 0, 0, 1, web_post_tl(), x, 0, 0, 1, web_post_tr())
    for i in range(ncols - 1):
        x = i + 1
        shape += key_wall_brace(x, 0, 0, 1, web_post_tl(), x, 0, 0, 1, web_post_tr())
        shape += key_wall_brace(
            x, 0, 0, 1, web_post_tl(), x - 1, 0, 0, 1, web_post_tr()
        )
    shape += key_wall_brace(
        lastcol, 0, 0, 1, web_post_tr(), lastcol, 0, 1, 0, web_post_tr()
    )
    return shape

def z_back_wall(column):
    shape = key_wall_brace(column, 0, 0, 1, web_post_tl(), column, 0, 0, 1, web_post_tr())
    # if column > 0:
    shape += key_wall_brace(column-1, 0, 0, 1, web_post_tr(), column, 0, 0, 1, web_post_tl(), True, True)

    return shape

def right_wall():
    y = 0
    shape = key_wall_brace(
        lastcol, y, 1, 0, web_post_tr(), lastcol, y, 1, 0, web_post_br()
    )
    for i in range(lastrow - 1):
        y = i + 1
        shape += key_wall_brace(
            lastcol, y, 1, 0, web_post_tr(), lastcol, y, 1, 0, web_post_br()
        )
        shape += key_wall_brace(
            lastcol, y, 1, 0, web_post_br(), lastcol, y - 1, 1, 0, web_post_tr()
        )
    shape += key_wall_brace(
        lastcol,
        cornerrow,
        0,
        -1,
        web_post_br(),
        lastcol,
        cornerrow,
        1,
        0,
        web_post_br(),
    )
    return shape


def left_wall():
    shape = wall_brace(
        (lambda sh: key_place(sh, 0, 0)),
        0,
        1,
        web_post_tl(),
        (lambda sh: left_key_place(sh, 0, 1)),
        0,
        1,
        web_post(),
    )

    shape += wall_brace(
        (lambda sh: left_key_place(sh, 0, 1)),
        0,
        1,
        web_post(),
        (lambda sh: left_key_place(sh, 0, 1)),
        -1,
        0,
        web_post(),
    )

    for i in range(lastrow):
        y = i
        temp_shape1 = wall_brace(
            (lambda sh: left_key_place(sh, y, 1)),
            -1,
            0,
            web_post(),
            (lambda sh: left_key_place(sh, y, -1)),
            -1,
            0,
            web_post(),
        )
        temp_shape2 = sl.hull()(
            key_place(web_post_tl(), 0, y),
            key_place(web_post_bl(), 0, y),
            left_key_place(web_post(), y, 1),
            left_key_place(web_post(), y, -1),
        )
        shape += temp_shape1 + temp_shape2

    for i in range(lastrow - 1):
        y = i + 1
        temp_shape1 = wall_brace(
            (lambda sh: left_key_place(sh, y - 1, -1)),
            -1,
            0,
            web_post(),
            (lambda sh: left_key_place(sh, y, 1)),
            -1,
            0,
            web_post(),
        )
        temp_shape2 = sl.hull()(
            key_place(web_post_tl(), 0, y),
            key_place(web_post_bl(), 0, y - 1),
            left_key_place(web_post(), y, 1),
            left_key_place(web_post(), y - 1, -1),
        )
        shape += temp_shape1 + temp_shape2

    return shape


def front_wall():
    shape = key_wall_brace(
        lastcol, 0, 0, 1, web_post_tr(), lastcol, 0, 1, 0, web_post_tr()
    )
    shape += key_wall_brace(
        3, lastrow, 0, -1, web_post_bl(), 3, lastrow, 0.5, -1, web_post_br()
    )
    shape += key_wall_brace(
        3, lastrow, 0.5, -1, web_post_br(), 4, cornerrow, 1, -1, web_post_bl()
    )
    for i in range(ncols - 4):
        x = i + 4
        shape += key_wall_brace(
            x, cornerrow, 0, -1, web_post_bl(), x, cornerrow, 0, -1, web_post_br()
        )
    for i in range(ncols - 5):
        x = i + 5
        shape += key_wall_brace(
            x, cornerrow, 0, -1, web_post_bl(), x - 1, cornerrow, 0, -1, web_post_br()
        )

    return shape

def z_front_wall(column):
    shape = key_wall_brace(
            column, cornerrow, 0, -1, web_post_bl(), column, cornerrow, 0, -1, web_post_br()
        )
    # if column > 0:
    shape += key_wall_brace(column-1, cornerrow, 0, -1, web_post_br(), column, cornerrow, 0, -1, web_post_bl(), True, True)

    if column == 2:
        shape += sl.translate([-2.2, 0, 0])(z_thumb_connector(0, -1, (lambda pos: key_position(pos, column, cornerrow)))) # TODO fix the connector overlap instead of artificial offset

    return shape

def z_thumb_walls():
    shape = wall_brace(thumb_tr_place, 1, -1, web_post_br(), thumb_tr_place, 1.4, 0, web_post_tr())
    shape += wall_brace(thumb_ml_place, -1, 0, web_post_bl(), thumb_ml_place, -1, 1, web_post_tl())
    shape += wall_brace(
        thumb_ml_place, -1, 0, web_post_bl(),
        (lambda shape: sl.translate ([0,0, -30])(thumb_tr_place(shape))), 1, -1, web_post_br(), True)

    # use vertical connector
    shape += wall_brace(
        thumb_ml_place, -1, 1, web_post_tl(),
        (lambda shape: sl.translate([0, 0, -30])(key_place(shape, 0, cornerrow))), 0, -1, web_post_bl(),
        True,
        None,
        (lambda pos: key_position(pos, -1, cornerrow)),
        True
        )

    shape +=  sl.translate([2.6, 0, 0])(z_thumb_connector(0, -1, (lambda pos: key_position(pos, 2, cornerrow)), True))

    return shape

def thumb_walls():
    # thumb, walls
    shape = wall_brace(
        thumb_tr_place, 0, -1, web_post_bl(), thumb_tr_place, 0, -1, web_post_br()
    )
    shape += wall_brace(
        thumb_tl_place, 0, -1, web_post_bl(), thumb_tr_place, 0, -1, web_post_bl()
    )
    shape += wall_brace(
        thumb_ml_place, -1, -1, web_post_bl(), thumb_tl_place, 0, -1, web_post_bl(),
    )
    shape += wall_brace(
        thumb_ml_place, -0.3, 1, web_post_tr(), thumb_ml_place, -1, 1, web_post_tl()
    )
    shape += wall_brace(
        thumb_ml_place, -1, 1, web_post_tl(), thumb_ml_place, -1, -1, web_post_bl()
    )
    shape += wall_brace(
        thumb_tr_place,
        0,
        -1,
        web_post_br(),
        (lambda sh: key_place(sh, 3, lastrow)),
        0,
        -1,
        web_post_bl(),
    )

    return shape


def thumb_connection2():
    # clunky bit on the top left thumb connection  (normal connectors don't work well)
    shape = bottom_hull(
        [
            left_key_place(
                sl.translate(wall_locate2(-1, 0))(web_post()), cornerrow, -1
            ),
            left_key_place(
                sl.translate(wall_locate3(-1, 0))(web_post()), cornerrow, -1
            ),
            thumb_ml_place(sl.translate(wall_locate2(-0.3, 1))(web_post_tr())),
            thumb_ml_place(sl.translate(wall_locate3(-0.3, 1))(web_post_tr())),
        ]
    )
    
    return shape
    
def thumb_connection():
    # clunky bit on the top left thumb connection  (normal connectors don't work well)
    shape = bottom_hull(
        [
            left_key_place(
                sl.translate(wall_locate2(-1, 0))(web_post()), cornerrow, -1
            ),
            left_key_place(
                sl.translate(wall_locate3(-1, 0))(web_post()), cornerrow, -1
            ),
            thumb_ml_place(sl.translate(wall_locate2(-0.3, 1))(web_post_tr())),
            thumb_ml_place(sl.translate(wall_locate3(-0.3, 1))(web_post_tr())),
        ]
    )

    shape += sl.hull()(
        [
            left_key_place(
                sl.translate(wall_locate2(-1, 0))(web_post()), cornerrow, -1
            ),
            left_key_place(
                sl.translate(wall_locate3(-1, 0))(web_post()), cornerrow, -1
            ),
            thumb_ml_place(sl.translate(wall_locate2(-0.3, 1))(web_post_tr())),
            thumb_ml_place(sl.translate(wall_locate3(-0.3, 1))(web_post_tr())),
            thumb_tl_place(web_post_tl()),
        ]
    )

    shape += sl.hull()(
        [
            left_key_place(web_post(), cornerrow, -1),
            left_key_place(
                sl.translate(wall_locate1(-1, 0))(web_post()), cornerrow, -1
            ),
            left_key_place(
                sl.translate(wall_locate2(-1, 0))(web_post()), cornerrow, -1
            ),
            left_key_place(
                sl.translate(wall_locate3(-1, 0))(web_post()), cornerrow, -1
            ),
            thumb_tl_place(web_post_tl()),
        ]
    )

    shape += sl.hull()(
        [
            left_key_place(web_post(), cornerrow, -1),
            left_key_place(
                sl.translate(wall_locate1(-1, 0))(web_post()), cornerrow, -1
            ),
            key_place(web_post_bl(), 0, cornerrow),
            key_place(sl.translate(wall_locate1(-1, 0))(web_post_bl()), 0, cornerrow),
            thumb_tl_place(web_post_tl()),
        ]
    )

    shape += sl.hull()(
        [
            thumb_ml_place(web_post_tr()),
            thumb_ml_place(sl.translate(wall_locate1(-0.3, 1))(web_post_tr())),
            thumb_ml_place(sl.translate(wall_locate2(-0.3, 1))(web_post_tr())),
            thumb_ml_place(sl.translate(wall_locate3(-0.3, 1))(web_post_tr())),
            thumb_tl_place(web_post_tl()),
        ]
    )

    return shape


def case_walls():
    return (
        back_wall()
        + left_wall()
        + right_wall()
        + front_wall()
    )

def z_case_walls(column):
    return (
        z_back_wall(column)
        # + left_wall()
        # + right_wall()
        + z_front_wall(column)
    )

def case_walls_t():
    return (
        thumb_walls()
        + thumb_connection()
    )

rj9_start = list(
    np.array([0, -3, 0])
    + np.array(
        key_position(
            list(np.array(wall_locate3(0, 1)) + np.array([0, (mount_height / 2), 0])),
            0,
            0,
        )
    )
)

rj9_position = [rj9_start[0], rj9_start[1], 11]


def rj9_cube():
    return sl.cube([14.78, 13, 22.38], center=True)


def rj9_space():
    return sl.translate(rj9_position)(rj9_cube())


def rj9_holder():
    shape = sl.union()(
        sl.translate([0, 2, 0])(sl.cube([10.78, 9, 18.38], center=True)),
        sl.translate([0, 0, 5])(sl.cube([10.78, 13, 5], center=True)),
    )
    shape = sl.difference()(rj9_cube(), shape)
    shape = sl.translate(rj9_position)(shape)
    return shape


usb_holder_position = key_position(
    list(np.array(wall_locate2(0, 1)) + np.array([0, (mount_height / 2), 0])), 1, 0
)
usb_holder_size = [6.5, 10.0, 13.6]
usb_holder_thickness = 4


def usb_holder():
    shape = sl.cube(
        [
            usb_holder_size[0] + usb_holder_thickness,
            usb_holder_size[1],
            usb_holder_size[2] + usb_holder_thickness,
        ],
        center=True,
    )
    shape = sl.translate(
        [
            usb_holder_position[0],
            usb_holder_position[1],
            (usb_holder_size[2] + usb_holder_thickness) / 2,
        ]
    )(shape)
    return shape


def usb_holder_hole():
    shape = sl.cube(usb_holder_size, center=True)
    shape = sl.translate(
        [
            usb_holder_position[0],
            usb_holder_position[1],
            (usb_holder_size[2] + usb_holder_thickness) / 2,
        ]
    )(shape)
    return shape


teensy_width = 20
teensy_height = 12
teensy_length = 33
teensy2_length = 53
teensy_pcb_thickness = 2
teensy_holder_width = 7 + teensy_pcb_thickness
teensy_holder_height = 6 + teensy_width
teensy_offset_height = 5
teensy_holder_top_length = 18
teensy_top_xy = key_position(wall_locate3(-1, 0), 0, centerrow - 1)
teensy_bot_xy = key_position(wall_locate3(-1, 0), 0, centerrow + 1)
teensy_holder_length = teensy_top_xy[1] - teensy_bot_xy[1]
teensy_holder_offset = -teensy_holder_length / 2
teensy_holder_top_offset = (teensy_holder_top_length / 2) - teensy_holder_length


def teensy_holder():
    s1 = sl.cube([3, teensy_holder_length, 6 + teensy_width], center=True)
    s1 = sl.translate([1.5, teensy_holder_offset, 0])(s1)

    s2 = sl.cube([teensy_pcb_thickness, teensy_holder_length, 3], center=True)
    s2 = sl.translate(
        [
            (teensy_pcb_thickness / 2) + 3,
            teensy_holder_offset,
            -1.5 - (teensy_width / 2),
        ]
    )(s2)

    s3 = sl.cube([teensy_pcb_thickness, teensy_holder_top_length, 3], center=True)
    s3 = sl.translate(
        [
            (teensy_pcb_thickness / 2) + 3,
            teensy_holder_top_offset,
            1.5 + (teensy_width / 2),
        ]
    )(s3)

    s4 = sl.cube([4, teensy_holder_top_length, 4], center=True)
    s4 = sl.translate(
        [teensy_pcb_thickness + 5, teensy_holder_top_offset, 1 + (teensy_width / 2)]
    )(s4)

    shape = sl.union()(s1, s2, s3, s4)

    shape = sl.translate([-teensy_holder_width, 0, 0])(shape)
    shape = sl.translate([-1.4, 0, 0])(shape)
    shape = sl.translate(
        [teensy_top_xy[0], teensy_top_xy[1] - 1, (6 + teensy_width) / 2]
    )(shape)

    return shape


def screw_insert_shape(bottom_radius, top_radius, height):
    shape = sl.union()(
        sl.cylinder(r1=bottom_radius, r2=top_radius, h=height, center=True),
        sl.translate([0, 0, (height / 2)])(sl.sphere(top_radius)),
    )
    return shape


def screw_insert(column, row, bottom_radius, top_radius, height):
    shift_right = column == lastcol
    shift_left = column == 0
    shift_up = (not (shift_right or shift_left)) and (row == 0)
    shift_down = (not (shift_right or shift_left)) and (row >= lastrow)

    if shift_up:
        position = key_position(
            list(np.array(wall_locate2(0, 1)) + np.array([0, (mount_height / 2), 0])),
            column,
            row,
        )
    elif shift_down:
        position = key_position(
            list(np.array(wall_locate2(0, -1)) - np.array([0, (mount_height / 2), 0])),
            column,
            row,
        )
    elif shift_left:
        position = list(
            np.array(left_key_position(row, 0)) + np.array(wall_locate3(-1, 0))
        )
    else:
        position = key_position(
            list(np.array(wall_locate2(1, 0)) + np.array([(mount_height / 2), 0, 0])),
            column,
            row,
        )

    shape = screw_insert_shape(bottom_radius, top_radius, height)
    shape = sl.translate((position[0], position[1], height / 2))(shape)

    return shape


def screw_insert_all_shapes(bottom_radius, top_radius, height):
    shape = sl.union()(
        screw_insert(0, 0, bottom_radius, top_radius, height),
        screw_insert(0, lastrow, bottom_radius, top_radius, height),
        screw_insert(2, lastrow + 0.3, bottom_radius, top_radius, height),
        screw_insert(3, 0, bottom_radius, top_radius, height),
        screw_insert(lastcol, 1, bottom_radius, top_radius, height),
    )

    return shape


screw_insert_height = 3.8
screw_insert_bottom_radius = 5.31 / 2
screw_insert_top_radius = 5.1 / 2
screw_insert_holes = screw_insert_all_shapes(
    screw_insert_bottom_radius, screw_insert_top_radius, screw_insert_height
)
screw_insert_outers = screw_insert_all_shapes(
    screw_insert_bottom_radius + 1.6,
    screw_insert_top_radius + 1.6,
    screw_insert_height + 1.5,
)
screw_insert_screw_holes = screw_insert_all_shapes(1.7, 1.7, 350)

wire_post_height = 7
wire_post_overhang = 3.5
wire_post_diameter = 2.6


def wire_post(direction, offset):
    s1 = sl.cube(
        [wire_post_diameter, wire_post_diameter, wire_post_height], center=True
    )
    s1 = sl.translate([0, -wire_post_diameter * 0.5 * direction, 0])(s1)

    s2 = sl.cube(
        [wire_post_diameter, wire_post_overhang, wire_post_diameter], center=True
    )
    s2 = sl.translate(
        [0, -wire_post_overhang * 0.5 * direction, -wire_post_height / 2]
    )(s2)

    shape = sl.union()(s1, s2)
    shape = sl.translate([0, -offset, (-wire_post_height / 2) + 3])(shape)
    shape = sl.rotate(-alpha / 2, [1, 0, 0])(shape)
    shape = sl.translate([3, -mount_height / 2, 0])(shape)

    return shape


def wire_posts():
    shape = thumb_ml_place(sl.translate([-5, 0, -2])(wire_post(1, 0)))
    shape += thumb_ml_place(sl.translate([0, 0, -2.5])(wire_post(-1, 6)))
    shape += thumb_ml_place(sl.translate([5, 0, -2])(wire_post(1, 0)))

    for column in range(lastcol):
        for row in range(lastrow - 1):
            shape += sl.union()(
                key_place(sl.translate([-5, 0, 0])(wire_post(1, 0)), column, row),
                key_place(sl.translate([0, 0, 0])(wire_post(-1, 6)), column, row),
                key_place(sl.translate([5, 0, 0])(wire_post(1, 0)), column, row),
            )
    return shape


def model_right():
    shape = sl.union()(key_holes(), connectors(), thumb_connectors2(),)
    
    # st = sl.union ()(thumb(), thumb_connectors(), case_walls_t(),)

    s2 = sl.union()(case_walls(),# screw_insert_outers(), teensy_holder(), usb_holder(),
    )

    #s2 = sl.difference()(s2, rj9_space(), usb_holder_hole(), screw_insert_holes())

    shape = sl.union()(shape, s2)
    #shape = st

    shape -= sl.translate([0, 0, -20])(sl.cube([350, 350, 40], center=True))
    return shape

def z_model_right(column):
    zs = sl.union()(
        z_key_holes(column),
        z_connectors(column),
        z_thumb_connectors2(column),
        z_case_walls(column))

    zs -= sl.translate([0, 0, -20])(sl.cube([350, 350, 40], center=True))

    return zs

def z_model_thumb_right():
    shape = sl.union ()(
        thumb(), 
        thumb_connectors(False),
        z_thumb_walls(),
        # case_walls_t(),
        )
    shape -= sl.translate([0, 0, -20])(sl.cube([350, 350, 40], center=True))
	
    return shape

def model_thumb_right():
    shape = sl.union ()(
        thumb(), 
        thumb_connectors(),
        case_walls_t(),
        )
    shape -= sl.translate([0, 0, -20])(sl.cube([350, 350, 40], center=True))
	
    return shape

for column in range(ncols):
    p = path.join(r"..", "things", r"right_z"+str(column)+r"_py.scad")
    sl.scad_render_to_file(z_model_right(column), p)
sl.scad_render_to_file(z_model_thumb_right(), path.join(r"..", "things", r"right_zthumb_py.scad"))

combined_z = []
for column in range(ncols):
    combined_z += z_model_right(column)
combined_z += z_model_thumb_right()
sl.scad_render_to_file(sl.union()(combined_z), path.join(r"..", "things", r"right_all_py.scad"))

sl.scad_render_to_file(model_right(), path.join(r"..", "things", r"right_py.scad"))
sl.scad_render_to_file(model_thumb_right(), path.join(r"..", "things", r"right_thumb_py.scad"))

sl.scad_render_to_file(
    sl.mirror([-1, 0, 0])(model_right()), path.join(r"..", "things", r"left_py.scad")
)
sl.scad_render_to_file(
    sl.mirror([-1, 0, 0])(model_thumb_right()), path.join(r"..", "things", r"left_thumb_py.scad")
)


def baseplate():
    shape = sl.union()(
        case_walls(),
        teensy_holder(),
        # rj9_holder(),
        screw_insert_outers(),
    )

    tool = sl.translate([0, 0, -10])(screw_insert_screw_holes())

    shape = shape - tool

    shape = sl.translate([0, 0, -0.1])(shape)

    return sl.projection(cut=True)(shape)


sl.scad_render_to_file(baseplate(), path.join(r"..", "things", r"plate_py.scad"))
