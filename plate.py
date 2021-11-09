import math
import bio96
import plateGUI

#well='C3'
#x=92833
#y=48856
#z=9877.375

class layout:
    def __init__(self, num_wells):
        self.num_wells = num_wells
        self.columns = int(math.sqrt((self.num_wells/6))*3)
        self.rows = int(math.sqrt((self.num_wells/6))*2)
        if num_wells == 96:
            self.spacing = 9000
            self.plate_bottom = 4313.65
            self.reference = ('C3',92833,48856)

        elif num_wells == 24:
            self.spacing = 19300
            self.plate_bottom = 3000.0   
            self.reference = ('D6',11056,5610)
        
        else:
            self.spacing = None
            self.plate_bottom = None   
            self.reference = None


        #self.spacing = self.getSpacing()
        self.position_grid = self.make_position_grid()
    
    def make_position_grid(self):
        position_grid = {}
        for row in range(0, self.rows, 1):
            for col in range (0, self.columns, 1):
                well_label = bio96.util.well0_from_well(bio96.util.well_from_ij(row,col))
                position_grid[well_label] = self.make_position_from_label(well_label)
        return position_grid

    def make_position_from_label(self, well_label):
        row_ref,col_ref = bio96.util.ij_from_well(self.reference[0])
        x_ref_pos, y_ref_pos = self.reference[1], self.reference[2]
        row, col = bio96.util.ij_from_well(well_label) 
        row_offset = row_ref - row
        col_offset = col_ref - col
        x_pos =  (col_offset*self.spacing) + x_ref_pos
        y_pos =  (row_offset*self.spacing) + y_ref_pos
        return (x_pos,y_pos)
    
    def get_pos_label(self,well_label):
        return self.position_grid[well_label]
    
    def get_pos_ij(self,i,j):
        return self.position_grid[bio96.util.well0_from_well(bio96.util.well_from_ij(i,j))]
    
    def get_sites(self, x,y, num_sites, ctrl):
        tile_size = int(math.sqrt(num_sites))
        tile_offset_x = ctrl.core.get_image_width() * ctrl.pixelStageCalibX/2
        tile_offset_y = ctrl.core.get_image_height() * ctrl.pixelStageCalibY
        tile_pos = []
        tile_offset_start_x = -(tile_size*tile_offset_x/1) 
        tile_offset_start_y = -(tile_size*tile_offset_y/2) 
        for ind_y in range(tile_size-1,-1,-1):
            row = []
            for ind_x in range(tile_size-1,-1,-1):
              row.append((tile_offset_start_x+(ind_x*tile_offset_x)+x, tile_offset_start_y+(ind_y*tile_offset_y)+y))
            tile_pos.append(row)
        return tile_pos



