import scriptcontext
import utility as rhutil
import Rhino
import System.Enum

def __viewhelper( view ):
  foundView=None
  if( view==None ): foundView = scriptcontext.doc.Views.ActiveView
  if( foundView==None ):
    allviews = scriptcontext.doc.Views.GetViewList(True, True)
    view_id = rhutil.coerceguid(view)
    for item in allviews:
      if( view_id!=None ):
        if( item.MainViewport.Id == view_id ):
          foundView = item
          break
      elif( item.MainViewport.Name == view ):
        foundView = item
        break
  return foundView

def AddDetail(layout_id, corner1, corner2, title=None, projection=1):
    """
    Adds a new detail view to an existing layout view
    Parameters:
      layout_id = identifier of an existing layout
      corner1, corner2 = 2d corners of the detail in the layout's unit system
      title[opt] = title of the new detail
      projection[opt] = type of initial view projection for the detail
          1 = parallel top view
          2 = parallel bottom view
          3 = parallel left view
          4 = parallel right view
          5 = parallel front view
          6 = parallel back view
          7 = perspective view
    Returns:
      identifier of the newly created detial on success
      None on error
    """
    layout_id = rhutil.coerceguid(layout_id)
    corner1 = rhutil.coerce2dpoint(corner1)
    corner2 = rhutil.coerce2dpoint(corner2)
    if( layout_id==None or corner1==None or corner2==None or projection<1 or projection>7):
        return scriptcontext.errorhandler()
    layout = scriptcontext.doc.Views.Find(layout_id)
    if( layout==None ): return scriptcontext.errorhandler()
    projection = System.Enum.ToObject(Rhino.Display.DefinedViewportProjection, projection)
    detail = layout.AddDetailView(title, corner1, corner2, projection)
    if( detail==None ): return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return detail.Id

def AddLayout(title=None, size=None):
    """
    Adds a new page layout view
    Parameters:
      title[opt] = title of new layout
      size[opt] = width and height of paper for the new layout
    Returns:
      id of new layout on success
      None on error
    """
    page = None
    if( size==None ): page = scriptcontext.doc.Views.AddPageView(title)
    else: page = scriptcontext.doc.Views.AddPageView(title, size[0], size[1])
    if( page==None ): return scriptcontext.errorhandler()
    return page.MainViewport.Id

def AddNamedCPlane(cplane_name, view=None):
  """
  Adds a new named construction plane to the document
  Parameters:
    cplane_name: the name of the new named construction plane
    view: [opt] string or Guid. The title or identifier of the view from which to save
                the construction plane. If omitted, the current active view is used.
  Returns:
    name of the newly created construction plane if successful
    None on error
  """
  if( cplane_name==None or len(cplane_name)<1 ): return scriptcontext.errorhandler()
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  plane = view.MainViewport.ConstructionPlane()
  if( plane==None ): return scriptcontext.errorhandler()
  index = scriptcontext.doc.NamedConstructionPlanes.Add(cplane_name, plane)
  if( index<0 ): return scriptcontext.errorhandler()
  return cplane_name


def AddNamedView(name, view=None):
  """
  Adds a new named view to the document
  Parameters:
    name: the name of the new named view
    view: [opt] the title or identifier of the view to save. If omitted, the current
          active view is saved
  Returns:
    name fo the newly created named view if successful
    None on error
  """
  if( name==None or len(name)<1 ): return scriptcontext.errorhandler()
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  viewportId = view.MainViewport.Id
  index = scriptcontext.doc.NamedViews.Add(name, viewportId)
  if( index<0 ): return scriptcontext.errorhandler()
  return name

# [skipping for now] BackgroundBitmap
def CurrentDetail(layout, detail=None, return_name=True):
    """
    Returns or changes the current detail view in a page layout view
    Parameters:
      layout = title or identifier of an existing page layout view
      detail[opt] = title or identifier the the detail view to set
      return_name[opt] = return title if True, else return identifier
    Returns:
      if detail is not specified, the title or identifier of the current detail view
      if detail is specified, the title or identifier of the previous detail view
      None on error
    """
    layout_id = rhutil.coerceguid(layout)
    page = None
    if( layout_id==None ): page = scriptcontext.doc.Views.Find(layout, False)
    else: page = scriptcontext.doc.Views.Find(layout_id)
    if( page==None ): return scriptcontext.errorhandler()
    rc = None
    active_viewport = page.ActiveViewport
    if( return_name ): rc = active_viewport.Name
    else: rc = active_viewport.Id

    if( detail!=None ):
        id = rhutil.coerceguid(detail)
        if( (id!=None and id==page.MainViewport.Id) or (id==None and detail==page.MainViewport.Name) ):
            page.SetPageAsActive()
        else:
            if( id!=None ): page.SetActiveDetail(id)
            else: page.SetActiveDetail(detail, False)
    scriptcontext.doc.Views.Redraw()
    return rc

def CurrentView(view=None, return_name=True):
  """
  Returns or sets the currently active view
  Parameters:
    view: [opt] String or Guid. The title or identifier of the view to set current. If omitted,
          only the title or identifier of the current view is returned
    return_name: [opt] If True (default), then the name, or title, of the view is returned.
                 If False, then the identifier of the view is returned
  Returns:
    if the title is not specified, the title or identifier of the current view if successful
    if the title is specified, the title or identifier of the previous current view if successful
    None on error
  """
  rc = None
  if( return_name==True ):
    rc = scriptcontext.doc.Views.ActiveView.MainViewport.Name
  else:
    rc = scriptcontext.doc.Views.ActiveView.MainViewport.Id
  
  if( view!= None ):
    id = rhutil.coerceguid(view)
    rhview = None
    if( id!=None ):
      rhview = scriptcontext.doc.Views.Find(id)
    else:
      rhview = scriptcontext.doc.Views.Find(view, False)
    if( rhview==None ): return scriptcontext.errorhandler()
    scriptcontext.doc.Views.ActiveView = rhview
  return rc


def DeleteNamedCPlane(name):
  """
  Removes a named construction plane from the document
  Parameters:
    name: name of the construction plane to remove
  Returns:
    True or False indicating success or failure
  """
  return scriptcontext.doc.NamedConstructionPlanes.Delete(name)


def DeleteNamedView(name):
  """
  Removes a named view from the document
  Parameters:
    name: name of the named view to remove
  Returns:
    True or False indicating success or failure
  """
  return scriptcontext.doc.NamedViews.Delete(name)

def DetailLock( detail_id, lock=None ):
    """
    Returns or modifies the projection locked state of a detail
    Parameters:
      detail_id = identifier of a detail object
      lock[opt] = the new lock state
    Returns:
      if lock==None, the current detail projection locked state
      if lock is True or False, the previous detail projection locked state
      None on error
    """
    detail_id = rhutil.coerceguid(detail_id)
    if( detail_id==None ): return scriptcontext.errorhandler()
    detail = scriptcontext.doc.Objects.Find(detail_id)
    if( detail==None ): return scriptcontext.errohandler()
    rc = detail.DetailGeometry.IsProjectionLocked
    if( lock!=None and lock!=rc ):
        detail.DetailGeometry.IsProjectionLocked = lock
        detail.CommitChanges()
    return rc

# [skipping for now] DetailNames

def DetailScale( detail_id, model_length=None, page_length=None ):
    """
    Returns or modifies the scale of a detail object
    Parameters:
      detail_id = identifier of a detail object
      model_length[opt] = a length in the current model units
      page_length[opt] = a length in the current page units
    Returns:
      current page to model scale ratio if model_length and page_length are both None
      previous page to model scale ratio if model_length and page_length are values
      None on error
    """
    detail_id = rhutil.coerceguid(detail_id)
    if( detail_id==None ): return scriptcontext.errorhandler()
    detail = scriptcontext.doc.Objects.Find(detail_id)
    if( detail==None ): return scriptcontext.errohandler()
    rc = detail.DetailGeometry.PageToModelRatio
    if( model_length!=None or page_length!=None ):
        if( model_length==None or page_length==None ):
            return scriptcontext.errorhandler()
        model_units = scriptcontext.doc.ModelUnitSystem
        page_units = scriptcontext.doc.PageUnitSystem
        if( detail.DetailGeometry.SetScale(model_length, model_units, page_length, page_units) ):
            detail.CommitChanges()
            scriptcontext.doc.Views.Redraw()
    return rc
    

# [skipping for now] IsBackgroundBitmap

def IsDetail( layout, detail ):
  """
  Verifies that a detail view exists on a page layout view
  Parameters:
    layout: title or identifier of an existing page layout
    detail: title or identifier of an existing detail view
  Returns:
    True if detail is a detail view
    False if detail is not a detail view
    None on error
  """
  layout_id = rhutil.coerceguid(layout)
  views = scriptcontext.doc.Views.GetViewList(False, True)
  found_layout = None
  for view in views:
    if( layout_id!=None ):
      if( view.MainViewport.Id == layout_id ):
        found_layout = view
        break
    elif( view.MainViewport.Name == layout ):
      found_layout = view
      break
  # if we couldn't find a layout, this is an error
  if( found_layout==None ): return scriptcontext.errorhandler()
  detail_id = rhutil.coerceguid(detail)
  detail_views = view.GetDetailViews()
  if( details==None ): return False
  for detail_view in details:
    if( detail_id!=None ):
      if( detail_view.Id == detail_id ):
        return True
    else:
      if( detail_view.Name == detail ):
        return True
  return False


def IsLayout( layout ):
  """
  Verifies that a view is a page layout view
  Parameters:
    layout: title or identifier of an existing page layout view
  Returns:
    True if layout is a page layout view
    False is layout is a standard, model view
    None on error
  """
  layout_id = rhutil.coerceguid(layout)
  alllayouts = scriptcontext.doc.Views.GetViewList(False, True)
  for layoutview in alllayouts:
    if( layout_id!=None ):
      if( layoutview.MainViewport.Id == layout_id ):
        return True
    elif( layoutview.MainViewport.Name == layout ):
      return True
  allmodelviews = scriptcontext.doc.Views.GetViewList(True, False)
  for modelview in allmodelviews:
    if( layout_id!=None ):
      if( modelview.MainViewport.Id == layout_id ):
        return False
    elif( modelview.MainViewport.Name == layout ):
      return False
  return scriptcontext.errorhandler()


def IsView( view ):
  """
  Verifies that the specified view exists
  Parameters:
    view: title or identifier of the view
  Returns:
    True of False indicating success or failure
  """
  view_id = rhutil.coerceguid(view)
  if( view_id==None and view==None ): return False
  allviews = scriptcontext.doc.Views.GetViewList(True, True)
  for item in allviews:
    if( view_id!=None ):
      if( item.MainViewport.Id == view_id ):
        return True
    elif( item.MainViewport.Name == view ):
      return True
  return False


def IsViewCurrent(view):
  """
  Verifies that the specified view is the current, or active view
  Parameters:
    view: title or identifier of the view
  Returns:
    True of False indicating success or failure
  """
  activeview = scriptcontext.doc.Views.ActiveView
  view_id = rhutil.coerceguid(view)
  if( view_id!=None ):
    return (view_id==activeview.MainViewport.Id)
  return (view==activeview.MainViewport.Name)


def IsViewMaximized( view=None ):
  """
  Verifies that the specified view is maximized (enlarged so as to fill
  the entire Rhino window)
  Paramters:
    view: [opt] title or identifier of the view. If omitted, the current
          view is used
  Returns:
    True of False
  """
  view = __viewhelper(view)
  if( view==None ): return False
  return view.Maximized


def IsViewPerspective( view ):
  """
  Verifies that the specified view's projection is set to perspective
  Parameters:
    view: title or identifier of the view
  Returns:
    True of False
    None on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  return view.MainViewport.IsPerspectiveProjection


def IsViewTitleVisible( view=None ):
  """
  Verifies that the specified view's title window is visible
  Paramters:
    view: [opt] The title or identifier of the view. If omitted, the current
          active view is used
  Returns:
    True of False indicating success or failure
    None on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  return view.MainViewport.TitleVisible


# [skipping for now] IsWallpaper

def MaximizeRestoreView( view=None ):
  """
  Toggles a view's maximized/restore window state of the specified view
  Parameters:
    view: [opt] the title or identifier of the view. If omitted, the current
          active view is used
  Returns:
    None
  """
  view = __viewhelper(view)
  if( view!=None ):
    if( view.Maximized==True ):
      view.Maximized = False
    else:
      view.Maximized = True


def NamedCPlane( name ):
  """
  Returns the plane geometry of the specified named construction plane
  Parameters:
    name: the name of the construction plane
  Returns:
    a plane on success
    None on error
  """
  index = scriptcontext.doc.NamedConstructionPlanes.Find(name)
  if( index<0 ):
    return scriptcontext.doc.NamedConstructionPlanes[index].Plane
  return scriptcontext.errorhandler()


def NamedCPlanes():
  """
  Returns the names of all named construction planes in the document
  """
  rc = []
  count = scriptcontext.doc.NamedConstructionPlanes.Count
  for i in xrange(count):
    name = scriptcontext.doc.NamedConstructionPlanes[i].Name
    rc.append(name)
  return rc


def NamedViews():
  """
  Returns the names of all named views in the document
  """
  rc = []
  count = scriptcontext.doc.NamedViews.Count
  for i in xrange(count):
    name = scriptcontext.doc.NamedViews[i].Name
    rc.append(name)
  return rc


def RenameView( old_title, new_title ):
  """
  Changes the title of the specified view
  Parameters:
    old_title: the title or identifier of the view to rename
    new_title: the new title of the view
  Returns:
    the view's previous title if successful
    None on error
  """
  if( old_title==None or new_title==None ):
    return scriptcontext.errorhandler()
  old_id = rhutil.coerceguid(old_title)
  foundview = None
  allviews = scriptcontext.doc.Views.GetViewList(True, True)
  for view in allviews:
    if( old_id!=None ):
      if( view.MainViewport.Id == old_id ):
        foundview = view
        break
    elif( view.MainViewport.Name == old_title ):
      foundview = view
      break
  if( foundview==None ):
    return None
  old_title = foundview.MainViewport.Name
  foundview.MainViewport.Name = new_title
  return old_title


def RestoreNamedCPlane(cplane_name, view=None):
  """
  Restores a named construction plane to the specified view.
  Parameters:
    cplane_name: name of the construction plane to restore
    view: [opt] the title or identifier of the view. If omitted, the current
          active view is used
  Returns:
    name of the restored named construction plane if successful
    None if not successful or on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  index = scriptcontext.doc.NamedConstructionPlanes.Find(cplane_name)
  if( index<0 ): return scriptcontext.errorhandler()
  cplane = scriptcontext.doc.NamedConstructionPlanes[index]
  view.MainViewport.PushConstructionPlane(cplane)
  view.Redraw()
  return cplane_name


def RestoreNamedView(named_view, view=None, restore_bitmap=False):
  """
  Restores a named view to the specified view
  Parameters:
    named_view: name of the named view to restore
    view: [opt] title or id of the view to restore the named view. If omitted,
          the current active view is used
    restore_bitmap: [opt] restore the named view's background bitmap
  Returns:
    name of the restored view if successful
    None on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  index = scriptcontext.doc.NamedViews.Find(named_view)
  if( index<0 ): return scriptcontext.errorhandler()
  viewinfo = scriptcontext.doc.NamedViews[index]
  if( view.MainViewport.PushViewInfo( viewinfo, restore_bitmap ) ):
    view.Redraw()
    return view.Name
  return scriptcontext.errorhandler()


def RotateCamera(view=None, direction=0, angle=None):
  """
  Rotates a perspective-projection view's camera. See the RotateCamera command
  in the Rhino help file for more details
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
    direction: [opt] the direction to rotate the camera where 0=right, 1=left,
          2=down, 3=up
    angle: [opt] the angle to rotate. If omitted, the angle of rotation is specified
          by the "Increment in divisions of a circle" parameter specified in Options
          command's View tab
  Returns:
    True or False indicating success or failure
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  viewport = view.ActiveViewport
  if( angle==None ):
    angle = 2.0 * Rhino.RhinoMath.Pi / Rhino.ApplicationSettings.ViewSettings.RotateCircleIncrement
  else:
    angle = abs(angle)
    angle = Rhino.RhinoMath.ToRadians(angle)
  target_distance = (viewport.CameraLocation-viewport.CameraTarget) * viewport.CameraZ
  axis = viewport.CameraY
  if( direction==0 or direction==2 ):
    angle=-angle
  if( direction==0 or direction==1 ):
    if( Rhino.ApplicationSettings.ViewSettings.RotateToView==True ):
      axis = viewport.CameraY
    else:
      axis = Rhino.Geometry.Vector3d.ZAxis
  elif( direction==2 or direction==3 ):
    axis = viewport.CameraX
  else:
    return False
  
  if( Rhino.ApplicationSettings.ViewSettings.RotateReverseKeyboard ):
    angle=-angle

  rot = Rhino.Geometry.Transform.Rotation(angle, axis, Rhino.Geometry.Point3d.Origin)
  camUp = rot * viewport.CameraY
  camDir = -(rot * viewport.CameraZ)
  target = viewport.CameraLocation + target_distance*camDir
  viewport.SetCameraLocations(target, viewport.CameraLocation)
  viewport.CameraUp = camUp
  view.Redraw()
  return True


def RotateView(view=None, direction=0, angle=None):
  """
  Rotates a view. See the RotateView command in Rhino help file for more information
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
    direction: [opt] the direction to rotate the view where 0=right, 1=left,
          2=down, 3=up
    angle: [opt] the angle to rotate. If omitted, the angle of rotation is specified
          by the "Increment in divisions of a circle" parameter specified in Options
          command's View tab
  Returns:
    True or False indicating success or failure
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  viewport = view.ActiveViewport
  if( angle==None ):
    angle = 2.0 * Rhino.RhinoMath.Pi / Rhino.ApplicationSettings.ViewSettings.RotateCircleIncrement
  else:
    angle = abs(angle)
    angle = Rhino.RhinoMath.ToRadians(angle)
  
  if( Rhino.ApplicationSettings.ViewSettings.RotateReverseKeyboard ):
    angle = -angle
  
  if( direction==0 ):
    viewport.KeyboardRotate(True, angle)
  elif( direction==1 ):
    viewport.KeyboardRotate(True, -angle)
  elif( direction==2 ):
    viewport.KeyboardRotate(False, -angle)
  elif( direction==3 ):
    viewport.KeyboardRotate(False, angle)
  else:
    return False
  
  view.Redraw()
  return True


def ShowGrid(view=None, show=None):
  """
  Shows or hides a view's construction plane grid
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
    show: [opt] The grid state to set. If omitted, the current grid display state is returned
  Returns:
    If show is not specified, then the grid display state if successful
    If show is specified, then the previous grid display state if successful
    None on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  viewport = view.ActiveViewport
  rc = viewport.ConstructionGridVisible
  if( show!=None and rc!=show ):
    viewport.ConstructionGridVisible = show
    view.Redraw()
  return rc


def ShowGridAxes(view=None, show=None):
  """
  Shows or hides a view's construction plane grid axes.
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
    show: [opt] The state to set. If omitted, the current grid axes display state is returned
  Returns:
    If show is not specified, then the grid axes display state if successful
    If show is specified, then the previous grid axes display state if successful
    None on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  viewport = view.ActiveViewport
  rc = viewport.ConstructionAxesVisible
  if( show!=None and rc!=show ):
    viewport.ConstructionAxesVisible = show
    view.Redraw()
  return rc


def ShowViewTitle(view=None, show=True):
  """
  Shows or hides the title window of a view
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
    show: [opt] The state to set.
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  view.TitleVisible = show


def ShowWorldAxes(view=None, show=None):
  """
  Shows or hides a view's world axis icon
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
    show: [opt] The state to set.
  Returns:
    If show is not specified, then the world axes display state if successful
    If show is specified, then the previous world axes display state if successful
    None on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  viewport = view.ActiveViewport
  rc = viewport.WorldAxesVisible
  if( show!=None and rc!=show ):
    viewport.WorldAxesVisible = show
    view.Redraw()
  return rc


# [skipping for now] SynchronizeCPlanes

def TiltView(view=None, direction=0, angle=None):
  """
  Tilts a view by rotating the camera up vector. See the TiltView command in the Rhino
  help file for more details.
    view: [opt] title or id of the view. If omitted, the current active view is used
    direction: [opt] the direction to rotate the view where 0=right, 1=left
    angle: [opt] the angle to rotate. If omitted, the angle of rotation is specified
          by the "Increment in divisions of a circle" parameter specified in Options
          command's View tab
  Returns:
    True or False indicating success or failure
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  viewport = view.ActiveViewport
  if( angle==None ):
    angle = 2.0 * Rhino.RhinoMath.Pi / Rhino.ApplicationSettings.ViewSettings.RotateCircleIncrement
  else:
    angle = abs(angle)
    angle = Rhino.RhinoMath.ToRadians(angle)
  
  if( Rhino.ApplicationSettings.ViewSettings.RotateReverseKeyboard ):
    angle = -angle

  axis = viewport.CameraLocation - viewport.CameraTarget
  if( direction==0 ):
    viewport.Rotate(angle, axis, viewport.CameraLocation)
  elif( direction==1 ):
    viewport.Rotate(-angle, axis, viewport.CameraLocation)
  else:
    return False
  view.Redraw()
  return True


def ViewCamera(view=None, camera_location=None):
  """
  Returns or sets the camera location of the specified view
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
    camera_location: [opt] a 3D point identifying the new camera location. If omitted,
      the current camera location is returned
  Returns:
    If camera_location is not specified, the current camera location
    If camera_location is specified, the previous camera location
    None on error    
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  rc = view.ActiveViewport.CameraLocation
  if( camera_location==None ):
    return rc
  camera_location = rhutil.coerce3dpoint(camera_location)
  if( camera_location==None ): return scriptcontext.errorhandler()
  view.ActiveViewport.SetCameraLocation(camera_location, True)
  view.Redraw()
  return rc


def ViewCameraLens(view=None, length=None):
  """
  Returns or sets the 35mm camera lens length of the specified perspective
  projection view.
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
    length: [opt] the new 35mm camera lens length. If omitted, the previous 35mm camera lens
            length is returned
  Returns:
    If lens length is not specified, the current lens length if successful
    If lens length is specified, the previous lens length if successful
    None on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  rc = view.ActiveViewport.Camera35mmLensLength
  if( length==None ):
    return rc
  view.ActiveViewport.Camera35mmLensLength = length
  view.Redraw()
  return rc


def ViewCameraPlane(view=None):
  """
  Returns the orientation of a view's camera.
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
  Returns:
    the view's camera plane if successful
    None on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  rc = view.ActiveViewport.GetCameraFrame()
  if(rc[0]==False): return scriptcontext.errorhandler()
  return rc[1]


def ViewCameraTarget(view=None, camera=None, target=None):
  """
  Returns or sets the camera and target positions of the specified view
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
    camera: [opt] a 3d point identifying the new camera location. If both camera and
       target are not specified, the current camera and target locations are returned
    target: [opt] a 3d point identifying the new target location. If both camera and
       target are not specified, the current camera and target locations are returned
  Returns:
    if both camera and target are not specified, then the 3d points containing the
      current camera and target locations is returned
    if either camera or target are specified, then the 3d points containing the
      previous camera and target locations is returned
    None on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  rc = [view.ActiveViewport.CameraLocation, view.ActiveViewport.CameraTarget]
  camera = rhutil.coerce3dpoint(camera)
  target = rhutil.coerce3dpoint(target)
  if( camera==None and target==None ):
    return rc
  if( camera!=None and target!=None ):
    view.ActiveViewport.SetCameraLocations(target, camera)
  elif( camera==None ):
    view.ActiveViewport.SetCameraTarget(target, True)
  else:
    view.ActiveViewport.SetCameraLocation(camera, True)
  view.Redraw()
  return rc


def ViewCameraUp(view=None, up_vector=None):
  """
  Returns or sets the camera up direction of a specified
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
    up_vector: [opt] 3d vector identifying the new camera up direction
  Returns:
    if up_vector is not specified, then the current camera up direction
    if up_vector is specified, then the previous camera up direction
    None on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  rc = view.ActiveViewport.CameraUp
  if( up_vector==None ):
    return rc
  up_vector=rhutil.coerce3dvector(up_vector)
  if( up_vector==None ):
    return scriptcontext.errorhandler()
  view.ActiveViewport.CameraUp = up_vector
  view.Redraw()
  return rc


def ViewCPlane(view=None, plane=None):
  """
  Returns or sets the specified view's construction plane
  Parameters:
    view:  [opt] title or id of the view. If omitted, the current active view is used.
    plane: [opt] the new construction plane if setting
  Returns:
    If a construction plane is not specified, the current construction plane if successful.
    If a construction plane is specified, the previous construction plane if successful.
    None if not successful or on Error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  cplane = view.ActiveViewport.ConstructionPlane()
  plane = rhutil.coerceplane(plane)
  if( plane!=None ):
    view.ActiveViewport.SetConstructionPlane(plane)
    view.Redraw()
  return cplane

# [skipping for now] ViewDisplayMode
# [skipping for now] ViewDisplayModeEx
# [skipping for now] ViewDisplayModeName
# [skipping for now] ViewDisplayModes

def ViewNames(return_names=True, view_type=0):
  """
  Returns the names, or titles, or identifiers of all views in the document
  Parameters:
    return_names: [opt] if True then the names of the views are returned. If False, then
                  the identifiers of the views are returned
    view_type: [opt] the type of view to return
                     0 = standard model views
                     1 = page layout views
                     2 = both standard and page layout views
  Returns:
    list of the view names or identifiers on success
    None on error
  """
  standardviews = view_type!=1
  pageviews = view_type>0
  views = scriptcontext.doc.Views.GetViewList(standardviews, pageviews)
  if( views==None ): return scriptcontext.errorhandler()
  rc = list()
  for view in views:
    if( return_names==True ):
      rc.append( view.MainViewport.Name )
    else:
      rc.append( view.MainViewport.Id )
  return rc


def ViewNearCorners(view=None):
  """
  Returns the 3d corners of a view's near clipping plane rectangle. This function
  is useful in determining the "real world" size of a parallel-projected view
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
  Returns:
    list of 4 Point3d that define the corners of the rectangle (counter-clockwise order)
    None on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  return view.ActiveViewport.GetNearRect()


def ViewProjection(view=None, mode=None):
  """
  Returns or sets a view's projection mode. A view's projection mode can be either
  parallel or perspective
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
    mode: [opt] the projection mode (1=parallel, 2=perspective)
  Returns:
    if mode is not specified, the current projection mode for the specified view
    if mode is specified, the previous projection mode for the specified view
    None on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  viewport = view.ActiveViewport
  rc = 2
  if( viewport.IsParallelProjection ):
    rc = 1
  if( mode==None or mode==rc ):
    return rc
  if( mode==1 ):
    viewport.ChangeToParallelProjection(True)
  elif( mode==2 ):
    viewport.ChangeToPerspectiveProjection(True, 50)
  else:
    return None
  view.Redraw()
  return rc

def ViewRadius(view=None, radius=None):
  """
  Returns or sets the radius of a parallel-projected view. This function is useful
  when you need an absolute zoom factor for a parallel-projected view
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
    radius: [opt] the view radius
  Returns:
    if radius is not specified, the current view radius for the specified view
    if radius is specified, the previous view radius for the specified view
    None on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  viewport = view.ActiveViewport
  if( not viewport.IsParallelProjection ):
    return scriptcontext.errorhandler()
  fr = viewport.GetFrustum()
  frus_right = fr[2]
  frus_left = fr[1]
  old_radius = min(frus_left, frus_right)
  if( radius==None ):
    return old_radius
  magnification_factor = radius / old_radius
  d = 1.0 / magnification_factor
  viewport.Magnify(d)
  view.Redraw()
  return old_radius


def ViewSize(view=None):
  """
  Returns the width and height in pixels of the specified view
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
  Returns:
    tuple of two numbers idenfitying width and height
    None on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  cr = view.ClientRectangle
  return cr.Width, cr.Height


def ViewTarget(view=None, target=None):
  """
  Returns or sets the target location of the specified view
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
    target: [opt] 3d point identifying the new target location. If omitted, the current
      target location is returned
  Returns:
    is target is not specified, then the current target location
    is target is specified, then the previous target location
    None on error
  """
  view = __viewhelper(view)
  if( view==None ): return scriptcontext.errorhandler()
  viewport = view.ActiveViewport
  old_target = viewport.CameraTarget
  if( target==None ):
    return old_target
  target = rhutil.coerce3dpoint(target)
  if( target==None ): return scriptcontext.errorhandler()
  viewport.SetCameraTarget(target, True)
  view.Redraw()
  return old_target


def ViewTitle(view_id):
  """
  Returns the name, or title, of a given view's identifier
  Parameters:
    view_id: String or Guid. The identifier of the view
  Returns:
    name or title of the view on success
    None on error
  """
  view_id = rhutil.coerceguid(view_id)
  if(view_id == None): return scriptcontext.errorhandler()
  view = scriptcontext.doc.Views.Find(view_id)
  if(view == None): return scriptcontext.errorhandler()
  return view.MainViewport.Name

# [skipping for now] Wallpaper
# [skipping for now] WallpaperGrayScale
# [skipping for now] WallpaperHidden

def ZoomBoundingBox(bounding_box, view=None, all=False):
  """
  Zooms to the extents of a specified bounding box in the specified view
  Parameters:
    bounding_box: eight points that define the corners of a bounding box or a BoundingBox
    view: [opt] title or id of the view. If omitted, the current active view is used
    all: [opt] zoom extents in all views
  """
  bbox = rhutil.coerceboundingbox(bounding_box)
  if( bbox!=None ):
    if( all==True ):
      views = scriptcontext.doc.Views.GetViewList(True, True)
      for view in views:
        view.ZoomBoundingBox(bbox)
      scriptcontext.doc.Views.Redraw()
    else:
      view = __viewhelper(view)
      if( view!=None ):
        view.ActiveViewport.ZoomBoundingBox(bbox)
        view.Redraw()


def ZoomExtents(view=None, all=False):
  """
  Zooms to the extents of visible objects in the specified view
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
    all: [opt] zoom extents in all views
  """
  if( all==True ):
    views = scriptcontext.doc.Views.GetViewList(True, True)
    for view in views:
      view.ZoomExtents(False)
    scriptcontext.doc.Views.Redraw()
  else:
    view = __viewhelper(view)
    if( view!=None ):
      view.ActiveViewport.ZoomExtents(False)
      view.Redraw()


def ZoomSelected(view=None, all=False):
  """
  Zooms to the extents of selected objects in the specified view
  Parameters:
    view: [opt] title or id of the view. If omitted, the current active view is used
    all: [opt] zoom extents in all views
  """
  if( all==True ):
    views = scriptcontext.doc.Views.GetViewList(True, True)
    for view in views:
      view.ZoomExtents(True)
    scriptcontext.doc.Views.Redraw()
  else:
    view = __viewhelper(view)
    if( view!=None ):
      view.ActiveViewport.ZoomExtentsSelected()
      view.Redraw()
