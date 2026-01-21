// PARAMETERS
radius = 40;
height = 10;
rounding = 4;   // Corner rounding
$fn = 96;       // Smoothness
hole_radius = 8; // Radius of the drilled hole
hole_x = 25;    // X position of hole center
hole_y = 15;    // Y position of hole center

// Helper for arc points
function pie_arc_points(r, angle=90, n=32) = 
    [for(i=[0:n]) let(a=angle*i/n) [r*cos(a), r*sin(a)]];

// Pie wedge points
pie_pts = concat([[0,0]], pie_arc_points(radius, 90, $fn), [[0,0]]);

difference() {
    // The rounded quarter-pie
    linear_extrude(height=height)
        offset(r=rounding)
            polygon(points=pie_pts);

    // The "drilled" hole (vertical cylinder)
    translate([hole_x, hole_y, -1]) // -1 to guarantee it cuts all the way
        cylinder(r=hole_radius, h=height+2, $fn=64); // $fn=64 = smooth
}
