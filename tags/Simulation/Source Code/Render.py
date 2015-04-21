'''
Author: Martin Stolle

Description: Renders the scene into a Quadru.rip file. A program called Pixie
             can work with this file. Creates tif file for every frame.
NOTE: Currently not in used!
'''

def near_callback(args, geom1, geom2):
	"""
	Callback function for the collide() method.

	This function checks if the given geoms do collide and creates contact
	joints if they do.
	"""

	if (ode.areConnected(geom1.getBody(), geom2.getBody())):
		return

	# check if the objects collide
	contacts = ode.collide(geom1, geom2)

	# create contact joints
	world, contactgroup = args
	for c in contacts:
		c.setBounce(0.2)
		c.setMu(500) # 0-5 = very slippery, 50-500 = normal, 5000 = very sticky
		j = ode.ContactJoint(world, contactgroup, c)
		j.attach(geom1.getBody(), geom2.getBody())

def renderMode(frames):
    '''By executing this python script you will create quadru.rib file,
       That can be used by Pixie in order to render this simulation frame
       by frame. Use --help for further information.'''
    print 'Render %s frames' % frames
    
    # Set the output rib file
    renderer = "Quadru.rib"
    
    # Create the header
    cgkit.riutil.RiBegin(renderer)
    cgkit.riutil.RiuDefaultHeader()
    
    # Set the width & height for each frame
    width = 320
    height = 240
    frame = 0
    
    # Set the number of frames, iterations/frames ratio and number of iterations
    R = 4
    N = (int(frames) - 1)*R + 1
    
    cWorld = myWorld()
    cWorld.world.setERP(0.8)
    
    cRobot = Robot(cWorld.world, cWorld.space, 500)
        
    # A joint group for the contact joints that are generated whenever
    # two bodies collide
    contactgroup = ode.JointGroup()
    
    dt = 1.0/const.framerate
        
    for n in range(N):
        # Detect collisions and create contact joints
        cWorld.space.collide((cWorld.world, contactgroup), near_callback)
            
        # Simulation step
        cWorld.world.step(dt)
            
        # Remove all contact joints
        contactgroup.empty()
            
        if (n % R == 0):
            # Create a frame
            frame += 1
            filename = 'Quadru.%03d.tif' % frame
            print filename
     
            cgkit.riutil.RiFrameBegin(frame)
            # Set the projection
            cgkit.riutil.RiProjection(cgkit.riutil.RI_PERSPECTIVE, fov=22)
     
            # Create a view transformation and apply
            V = cgkit.cgtypes.mat4(1).lookAt(2.0*cgkit.cgtypes.vec3(-4, 6, -6),
                                             (0, 0.5, 0), up=(0, 1, 0))
            V = V.inverse()
            cgkit.riutil.RiTransform(V.toList())
     
            # Set the output file and frame format
            cgkit.riutil.RiDisplay(filename, cgkit.riutil.RI_FILE, cgkit.riutil.RI_RGBA)
            cgkit.riutil.RiFormat(width, height, 1.0)
     
            # Apply sampling
            cgkit.riutil.RiPixelSamples(4,4)
            cgkit.riutil.RiShadingInterpolation(cgkit.riutil.RI_SMOOTH)
     
            # Begin the world
            cgkit.riutil.RiWorldBegin()
            # Make objects visible to rays
            cgkit.riutil.RiDeclare("diffuse", "integer")
            cgkit.riutil.RiAttribute("visibility", "diffuse", 1)
            cgkit.riutil.RiDeclare("bias", "float")
            cgkit.riutil.RiAttribute("trace", "bias", 0.005)
            # Don't interpolate irradiance
            cgkit.riutil.RiDeclare("maxerror", "float")
            cgkit.riutil.RiAttribute("irradiance", "maxerror", 0.0)
            # Apply global illumination
            cgkit.riutil.RiDeclare("samples", "integer")
            cgkit.riutil.RiSurface("occsurf2", "samples", 256)
     
            # Create a white ground plane
            cgkit.riutil.RiAttributeBegin()
            cgkit.riutil.RiColor([ 0.9, 0.9, 0.9 ])
            cgkit.riutil.RiPolygon(P=[ -20, 0, 20, 20, 0, 20, 20, 0, -20, -20, 0, -20 ])
            cgkit.riutil.RiAttributeEnd()
     
            # Draw the bodies
            for b in cRobot.femur:
               renderBody(b)
            
            for b in cRobot.tibia:
                renderBody(b)
    
            renderBody(cRobot.body)
     
            # Complete the world & frame
            cgkit.riutil.RiWorldEnd()
            cgkit.riutil.RiFrameEnd()
    
    cgkit.riutil.RiEnd()
    
def renderBody(body):
    """
    Draw the body with Renderman primitives.
    """
    (x, y, z) = body.getPosition()
    R = body.getRotation()
    # Construct the transformation matrix
    T = cgkit.cgtypes.mat4()
    T[0,0] = R[0]
    T[0,1] = R[1]
    T[0,2] = R[2]
    T[1,0] = R[3]
    T[1,1] = R[4]
    T[1,2] = R[5]
    T[2,0] = R[6]
    T[2,1] = R[7]
    T[2,2] = R[8]
    T[3] = (x ,y ,z , 1.0)
    cgkit.riutil.RiTransformBegin()
    # Apply rotation & translation
    cgkit.riutil.RiTransform(T.toList())
    (sx, sy, sz) = body.boxsize
    # Draw the body
    cgkit.riutil.RiScale(sx, sy, sz)
    cgkit.riutil.RiAttributeBegin()
    cgkit.riutil.RiColor([ 1.0, 0.6, 0.0 ])
    cgkit.riutil.RiPolygon(P=[ -0.5,-0.5,-0.5, -0.5,-0.5, 0.5, -0.5, 0.5, 0.5, -0.5, 0.5,-0.5 ]) # left side
    cgkit.riutil.RiPolygon(P=[  0.5, 0.5,-0.5,  0.5, 0.5, 0.5,  0.5,-0.5, 0.5,  0.5,-0.5,-0.5 ]) # right side
    cgkit.riutil.RiPolygon(P=[ -0.5, 0.5,-0.5,  0.5, 0.5,-0.5,  0.5,-0.5,-0.5, -0.5,-0.5,-0.5 ]) # front side
    cgkit.riutil.RiPolygon(P=[ -0.5,-0.5, 0.5,  0.5,-0.5, 0.5,  0.5, 0.5, 0.5, -0.5, 0.5, 0.5 ]) # back side
    cgkit.riutil.RiPolygon(P=[ -0.5, 0.5, 0.5,  0.5, 0.5, 0.5,  0.5, 0.5,-0.5, -0.5, 0.5,-0.5 ]) # top
    cgkit.riutil.RiPolygon(P=[ -0.5,-0.5,-0.5,  0.5,-0.5,-0.5,  0.5,-0.5, 0.5, -0.5,-0.5, 0.5 ]) # bottom
    cgkit.riutil.RiAttributeEnd()
    cgkit.riutil.RiTransformEnd()