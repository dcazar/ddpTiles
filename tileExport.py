import os

mxdin = arcpy.GetParameterAsText(0)
folder = arcpy.GetParameterAsText(1)
tilingScheme = arcpy.GetParameterAsText(2)

#Change the values below to add or remove scales from the tile packages. The values should be copied directly from
#the XML ArcGIS_Online_Bing_Maps_Google_Maps. Make sure that all values are in between the max an min and update
#if necessary.

scales = "288895.277144;144447.638572;72223.819286;36111.909643;18055.954822;9027.977411"
mincachedscale = "288895.277144"
maxcachedscale = "9027.977411"

#Constants ---DO NOT ALTER THIS BLOCK---
mode = "RECREATE_ALL_TILES"
dataSource = mxdin
method = "IMPORT_SCHEME"
cacheType = "TILE_PACKAGE"
storageFormat = "COMPACT"
temp_lyr_name = "temp"
temp_ftr_name = "tmp_feature"
pof = folder + os.sep + "tile_pkgs"
areaofinterest = "#"

#Uncomment this line if using ArcGIS 10.4.1 or lower.
v = float(arcpy.GetInstallInfo()['Version'][:4])

if v < 10.5:
    arcpy.env.parallelProcessingFactor = "0"
    arcpy.AddMessage("Version lower than 10.5 detected, limited to 1 CPU")
else:
    arcpy.env.parallelProcessingFactor = ""
    arcpy.AddMessage("Version 10.5 or higher detected, using default CPUs")

#Check that tile scheme is an xml document.
schemExt = os.path.splitext(tilingScheme)[-1]
if schemExt == ".xml":
    arcpy.AddMessage("An XML file was passed to the tool.")
    pass
else:
    arcpy.AddError("File other than XML passed to tool. Select a valid XML tiling schema.")
    quit()

# Create tile package target Directory if don't exist
if not os.path.exists(pof):
    os.mkdir(pof)
    arcpy.AddMessage("Directory " + pof +  " Created ")
else:    
    arcpy.AddMessage("Directory " + pof +  " already exists")


#Layer manipulation requires that the mxd object be the current mxd
mxd = arcpy.mapping.MapDocument("CURRENT")
mxd.save()
ddp = mxd.dataDrivenPages
df = arcpy.mapping.ListDataFrames(mxd)[0]


#Iterate through all pages in the current mxd
for i in range(1, mxd.dataDrivenPages.pageCount + 1):
    mxd.dataDrivenPages.currentPageID = i
    row = mxd.dataDrivenPages.pageRow
    pageName = row.getValue(ddp.pageNameField.name)
    arcpy.AddMessage("Processing tile {0} of {1}".format(str(mxd.dataDrivenPages.currentPageID), str(mxd.dataDrivenPages.pageCount)))
    cacheName = pageName
    #Create a temporary layer for current dpp polygon and make a copy
    arcpy.MakeFeatureLayer_management(ddp.indexLayer,temp_lyr_name,where_clause=ddp.pageNameField.name+ " = " + "'" + pageName + "'")
    arcpy.CopyFeatures_management(temp_lyr_name,temp_ftr_name)
    #Turn off visibility and refresh view before exporting to cache
    arcpy.RefreshActiveView()
    arcpy.RefreshTOC()
    mxd.save()
    #Export to cache using the temporary ddp polygon feature as the aoi in the Tile Management tool
    arcpy.AddMessage("Creating cache for tile {0} of {1}".format(str(mxd.dataDrivenPages.currentPageID), str(mxd.dataDrivenPages.pageCount)))
    arcpy.ManageTileCache_management(folder, mode, cacheName, dataSource, method, tilingScheme,scales,
       temp_ftr_name,"", mincachedscale, maxcachedscale)
    cacheSource = folder + os.sep + cacheName + os.sep + df.name #name of tile cache folder is inherited from df
    cacheTarget = pof
    #Export tiles using aoi again
    arcpy.AddMessage("Exporting tile {0} of {1}".format(str(mxd.dataDrivenPages.currentPageID), str(mxd.dataDrivenPages.pageCount)))
    arcpy.ExportTileCache_management(cacheSource, cacheTarget, cacheName,
     cacheType,storageFormat,scales, temp_ftr_name)
    #Cleanup
    arcpy.Delete_management(temp_ftr_name)

    






    




