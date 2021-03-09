-- Taking some useful parts
-- https://github.com/rgrams/rendercam/blob/master/rendercam/rendercam.lua

-- ATM this stripped down version only has functions related to converting screen space to GUI space for positioning GUI nodes

local M = {}

-- GUI "transform" data - set in `calculate_gui_adjust_data` and used for screen-to-gui transforms in multiple places
--				Fit		(scale)		(offset)	Zoom						Stretch
M.guiAdjust = { [0] = {sx=1, sy=1, ox=0, oy=0}, [1] = {sx=1, sy=1, ox=0, oy=0}, [2] = {sx=1, sy=1, ox=0, oy=0} }
M.guiOffset = vmath.vector3()

-- GUI Adjust modes - these match up with the gui library properties (gui.ADJUST_FIT, etc.)
M.GUI_ADJUST_FIT = 0
M.GUI_ADJUST_ZOOM = 1
M.GUI_ADJUST_STRETCH = 2

-- Current window size
M.window = vmath.vector3() -- only set in `M.update_window_size`

-- Initial window size - set on init in render script
M.configWin = vmath.vector3()

function M.update_window_size(x, y)
	M.window.x = x;  M.window.y = y
end

-- M.window.x, M.window.y, M.configWin.x, M.configWin.y
local function calculate_gui_adjust_data(winX, winY, configX, configY)
	local sx, sy = winX / configX, winY / configY

	-- Fit
	local adj = M.guiAdjust[M.GUI_ADJUST_FIT]
	local scale = math.min(sx, sy)
	adj.sx = scale;  adj.sy = scale
	adj.ox = (winX - configX * adj.sx) * 0.5 / adj.sx
	adj.oy = (winY - configY * adj.sy) * 0.5 / adj.sy

	-- Zoom
	adj = M.guiAdjust[M.GUI_ADJUST_ZOOM]
	scale = math.max(sx, sy)
	adj.sx = scale;  adj.sy = scale
	adj.ox = (winX - configX * adj.sx) * 0.5 / adj.sx
	adj.oy = (winY - configY * adj.sy) * 0.5 / adj.sy

	-- Stretch
	adj = M.guiAdjust[M.GUI_ADJUST_STRETCH]
	adj.sx = sx;  adj.sy = sy
	-- distorts to fit window, offsets always zero
end

function M.screen_to_gui(x, y, adjust, isSize)
	if not isSize then
		x = x / M.guiAdjust[adjust].sx - M.guiAdjust[adjust].ox
		y = y / M.guiAdjust[adjust].sy - M.guiAdjust[adjust].oy
	else
		x = x / M.guiAdjust[adjust].sx
		y = y / M.guiAdjust[adjust].sy
	end
	return x, y
end

function M.screen_to_gui_pick(x, y)
	return x / M.guiAdjust[2].sx, y / M.guiAdjust[2].sy
end

function M.update()
	calculate_gui_adjust_data(M.window.x, M.window.y, M.configWin.x, M.configWin.y)
end


return M