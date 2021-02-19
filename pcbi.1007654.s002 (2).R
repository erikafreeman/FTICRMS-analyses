#https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007654
#https://emsl-computing.github.io/ftmsRanalysis/reference/

# install ftmsRanalysis #
#devtools::install_github("EMSL-Computing/ftmsRanalysis")
# install plotly for graphics #
#install.packages("plotly")
# if you wish to run the trelliscope part of the code, you must have 'datadr' and 'trelliscope' packages installed #
#install.packages("datadr")
#devtools::install_github("hafen/trelliscope")

# if you wish to mapp to MetaCyc you must install the MetaCycData package #
#devtools::install_github("EMSL-Computing/MetaCycData")
library(MetaCycData)
library(ftmsRanalysis)
library(datadr)
library(trelliscope)
library(plotly)
library(openxlsx) # for reading in xlsx data file, not necessary if you save sheets as .csvs

# directory where the data is saved, need to modify based on local filepath #
#filepath = "/home/erika/Desktop/pcbi.1007654.s001 (2).xlsx"
filepath = "/home/erika/Desktop/pandas_multiple1.xlsx"

#### format the data ####

# read in data #
edata = read.xlsx(filepath, sheet = 1)
fdata = read.xlsx(filepath, sheet = 2)
emeta = read.xlsx(filepath, sheet = 3)

# construct peakData object #
peak_data = as.peakData(e_data = edata, f_data = fdata, e_meta = emeta, edata_cname = "Mass", fdata_cname = "SampleID",
                         mass_cname = "Mass", c_cname = "C", h_cname = "H", o_cname = "O", n_cname = "N", s_cname = "S", p_cname = "P",
                         isotopic_cname = "C13", isotopic_notation = "1")


#### specify main effects relevant for grouping samples ####
# use location and crop/flora #
peak_data = group_designation(peak_data, main_effects = c("Slope", "Depth"))

# summarize data to get number of samples per group #
# Samples: 20, Molecules: 23060, Percent Missing: 81.739% #
summary(peak_data)

# plot the data #
plot(peak_data)

# plot of log2 peak intensity distribution for each sample #
plot(edata_transform(peak_data, "log2"), ylabel = "log2(Peak Intensity)", xlabel = "") 

# transform the data to presence/absence #
pa_data = edata_transform(peak_data, "pres")

# plot number of observed peaks for each sample #
plot(pa_data, ylabel = "Number of Observed Peaks", xlabel = "") 

#### calculate additional values for each peak ####

## calculate aromaticity, double bond equivalent, kendrick mass/defect, nominol oxidation state of carbon, and elemental ratios ##
pa_data = compound_calcs(pa_data, calc_fns = c("calc_aroma", "calc_dbe", "calc_kendrick", "calc_nosc", "calc_element_ratios"))

#### assign peak classes based on elemental ratios ####
# use boundary set 1 #
pa_data = assign_class(pa_data, boundary_set = "bs1")

# use boundary set 2 #
pa_data = assign_class(pa_data, boundary_set = "bs2")

#### assign elemental composition (which elements are present for each peak) ####
pa_data = assign_elemental_composition(pa_data)

#### filter the data ####

## mass filter ##
# create filter peaks based on mass #
mass_filt = mass_filter(pa_data)

# plot filter with potential minimum and maximum mass cutoffs #
plot(mass_filt, min_mass = 200, max_mass = 900)

# get numeric summary of the effect of the filter with these bounds #
summary(mass_filt, min_mass = 200, max_mass = 1000)

# apply filter to keep peaks with mass between 200 and 1000 #
pa_data = applyFilt(filter_object = mass_filt, ftmsObj = pa_data, min_mass = 200, max_mass = 1000)

summary(pa_data) # Samples: 20, Molecules: 19327, Percent Missing: 79.299% #

## molecule filter ##
# create filter based on number of samples for which peak was observed #
molecule_filt = molecule_filter(ftmsObj = pa_data)

# plot filter object with requiring 2 observations per peak #
plot(molecule_filt, min_num = 2, xlabel = "Minimum Number of Samples for which a Peak is Observed", ylabel = "Number of Peaks") 

# get numeric summary of the effect of the filter requiring at least two observations for a peak #
summary(molecule_filt, min_num = 2)

# apply filter to keep peaks observed in at least 2 samples or more #
pa_data = applyFilt(filter_object = molecule_filt, ftmsObj = pa_data, min_num = 2)

summary(pa_data) # Samples: 20, Molecules: 8427, Percent Missing: 58.990% #

## formula filter ##
# create filter based on whether a formula could be assigned to a peak #
formula_filt = formula_filter(ftmsObj = pa_data)

# plot filter object with effect of keeping only peaks with formula assigned #
plot(formula_filt, remove = "NoFormula", ylabel = "Number of Peaks")

# get numeric summary of the effect of filter if applied #
summary(formula_filt, remove = "NoFormula")

# apply filter to keep peaks with formula assigned #
pa_data = applyFilt(filter_object = formula_filt, ftmsObj = pa_data, remove = "NoFormula")

summary(pa_data) #Samples: 20, Molecules: 6498, Percent Missing: 54.242% #

## emeta filter -- can filter based on any column in e_meta ##

# create filter based on peak's modified aromaticity # 
# get the e_meta column name corresponding to modified aromaticity #
getModAromaColName(pa_data)

# construct filter #
modaroma_filt = emeta_filter(pa_data, getModAromaColName(pa_data))

# visualize the effect of filtering down to aromatic peaks (modified aromaticity >= 0.5) #
plot(modaroma_filt, min_val = 0.5)

# we won't apply filter here, but below is how to apply filter #
# pa_data = applyFilt(filter_object = modaroma_filt, icrData = pa_data, min_val = 0.5)

# construct filter based on peak class determined by boundary set 1 #
# get e_meta column name #
getBS1ColName(pa_data)

# construct filter #
bs1_filt = emeta_filter(pa_data, getBS1ColName(pa_data))

# visualize the effect of filtering down to carbohydrates and lignins only #
plot(bs1_filt, cats = c("Carbohydrate","Lignin"))

# we won't apply filter here, but below is how to apply filter #
# pa_data = applyFilt(filter_object = bs1_filt, icrData = pa_data, cats = c("Carbohydrate","Lignin"))

#### plot distribution of e_meta column by sample, for all samples --- doesn't currently work ####
# classesPlot()


#### Visualizations of one sample ####
# subset to the sample of interest #
em0011_data <- subset(pa_data, samples="EM0011_sample")

# get data summary and a look at e_data #
summary(em0011_data)
head(em0011_data$e_data)

# Van Krevelen Plot #
# By default, the points are colored according to peak class based on boundary set 1 #
vanKrevelenPlot(em0011_data, title="EM0011_sample")

# we can also color the points according to other meta data columns in the `e_meta` object #
# here we use NOSC #
vanKrevelenPlot(em0011_data, colorCName= getNOSCColName(em0011_data), legendTitle = "NOSC", title="EM0011_sample", showVKBounds = F)

# Kendrick Plot #
# By default, the points are colored according to peak class based on boundary set 1 #
# can color points by other columns in e_meta, as shown for the Van Krevelen plot #
kendrickPlot(em0011_data, title="") 

# we can also color the points according to other meta data columns in the `e_meta` object #
# here we use NOSC ratio #
kendrickPlot(em0011_data, colorCName= getNOSCColName(em0011_data), legendTitle = "NOSC", title="EM0011_sample")

# Histogram #
# We can also plot the distributions of any (numeric) column of meta-data (i.e. column of `e_meta`) #
# here we plot nominal oxidation state of carbon (NOSC) #
densityPlot(em0011_data, variable = getNOSCColName(em0011_data), plot_curve=TRUE, plot_hist=TRUE,
            title="") 

# It's also possible to plot just the histogram or just the density curve with this function with the `plot_hist` and `plot_curve` parameters. #
# here just plot histogram with no density curve #
densityPlot(em0011_data, variable = getNOSCColName(em0011_data), 
            title="NOSC for EM0011_sample", plot_hist=TRUE, plot_curve = FALSE, yaxis="count")

#### Experimental Group Plots ####
# get group data.frame based on defined groups previously specified by calling 'group_designation()' #
getGroupDF(pa_data)

# subset the data to a single group, valid values are in the 'Group' column of the group data.frame #
mich_switch_data = subset(pa_data, groups = "S_5")


densityPlot(mich_switch_data, variable = getModAromaColName(mich_switch_data), groups = NA, xlabel = "Modified Aromaticity")

vanKrevelenPlot(mich_switch_data)

# The `summarizeGroups` function calculates group-level summaries per peak, such as the number or proportion of samples in which peak is observed # 
getGroupSummaryFunctionNames()
ms_summarized = summarizeGroups(mich_switch_data, summary_functions = c("n_present", "prop_present"))

# The resulting object's `e_data` element contains one column per group, per summary function #
head(ms_summarized$e_data)
vanKrevelenPlot(ms_summarized, colorCName = "Michigan_Switchgrass_n_present", legendTitle = "Times Observed", showVKBounds = F, title = "")

### Comparison of Experimental Groups ####
# summarize number present and proportion present for all groups #
group_summary <- summarizeGroups(pa_data, summary_functions = c("n_present", "prop_present"))
head(group_summary$e_data)

# We can use the `densityPlot` function to compare distributions of some meta-data crop/flora type between Michigan groups. #
densityPlot(pa_data, samples=FALSE, groups=c("Michigan_Corn","Michigan_Switchgrass"), variable="NOSC", 
            title="") 
# We might also want to look at which peaks occur only in one group or another, versus those that appear in both groups. To do that, we perform a statistical test called the [G-Test](https://en.wikipedia.org/wiki/G-test). This test will tell us for each peak whether it appears in one group or both. #

### You need the R package 'datadr' beyond this point ###
# The first step is to create peakIcrData objects that each contain two groups to facilitate group comparisons #

byGroupComps <- divideByGroupComparisons(pa_data, 
                                         comparisons = "all")
# get list of group comparisons #
getKeys(byGroupComps)

# we're interested in Michigan Corn vs Switchgrass, so we'll pull that data #
byGroup <- byGroupComps[[1]]$value

# define a peak to be present for a group if it's seen in more than half of the samples, and unique if g-test p-value is less than 0.05 #
crop_unique <- summarizeGroupComparisons(byGroup, 
                                         summary_functions="uniqueness_gtest", 
                                         summary_function_params=list(
                                           uniqueness_gtest=list(pres_fn="nsamps", 
                                                                 pres_thresh=3, pvalue_thresh=0.05)))

tail(crop_unique$e_data)

# make van Krevelen plot of results #
vanKrevelenPlot(crop_unique, colorCName = "uniqueness_gtest", showVKBounds = F)


### create Trelliscope display of van Krevelen diagram for each sample ###
## You need the R package 'trelliscope' from this point on ##
bySample <- divideBySample(pa_data)
bySample

# Each element of `bySample` is a key/value pair. They key names correspond to the sample names, and may be used to index bySample to pull out a single element #
getKeys(bySample)[1:5]

bySample[["SampleID=EM0011_sample"]]


# Trelliscope relies on the user defining a *panel function* and a *cognostics function* that are applied to each subset of data. A panel function is simply a function that takes a data subset and constructs a plot (or panel) from it. Panel functions may construct plots in any plotting package used in R, including base R graphics, `ggplot2`, and plots that extend `htmlwidgets` such as `plotly`. Most of the plotting methods in `fticRanalysis` produce `plotly` plots.

# The `fticRanalysis` package provides a wrapper function (`panelFunctionGenerator`) which can be used with the packages plotting methods to make panel functions for Trelliscope.

# A cognostics function is a function that calculates summary statistics on each subset of data. These statistics are then provided in the user interface for sorting and filtering. Example cognostics could include data quantiles, related meta-data or even links to external web resources if desired. 

# There are a few cognostics functions in `fticRanalysis` designed to provide default cognostics relevant to Van Krevelen plots, Kendrick plots and density plots. These are called, respectively, `vanKrevelenCognostics`, `kendrickCognostics` and `densityCognostics`. Each of these functions is designed to accept parameters similar to their respective plotting functions (e.g. Van Krevelen boundary set, or which variable is used for density plots), and they each return a *function* which may be passed to Trelliscope. This function will be applied to each data subset individually. Cognostics function examples are shown below.

# In order to create a Trelliscope display, we need to define an output directory to store it. (The output will be a Shiny app, and may be then transferred to a Shiny server if desired.) For this vignette we'll just create a directory under R's temporary directory


vdbDir <- vdbConn(file.path(tempdir(), "trelliscope_vignette"), autoYes = TRUE)

# To produce a Van Krevelen plot of each sample, construct a panel function using `panelFunctionGenerator`. The output of `panelFunctionGenerator` is a function that will produce a plot when applied to a single value from `bySample`'s list of key-value pairs:


panelFn1 <- panelFunctionGenerator("vanKrevelenPlot", vkBoundarySet = "bs1")
panelFn1(bySample[[1]]$value)


# To apply the panel function to each sample and generate a Trelliscope *display*, use the `makeDisplay` command. 

makeDisplay(bySample, 
            panelFn=panelFn1,
            cogFn=vanKrevelenCognostics(vkBoundarySet="bs1"),
            name = "Van_Krevelen_plots_for_each_sample",
            group = "Sample",
            height = 700, width = 900)

# Use the `view()` command to open the Trelliscope app in a browser and browse through the plots. 
# Important: when returning to the R console after viewing a Trelliscope app, press Ctrl+C or Esc to return focus to the console.

# You may have noticed in the call to `panelFunctionGenerator` we provided a parameter (`vkBoundarySet`) that is a parameter to the `vanKrevelenPlot` function. This is how additional parameters beyond the `peakData` object may be provided. For example, we could choose to color the points by a meta-data column such as NOSC. Trelliscope is designed to allow multiple displays (or sets of plots) in one session.

# In the `makeDisplay` call above, also note the use of `vanKrevelenCognostics` with the same `vkBoundarySet` parameter used above to define `panelFn1`.

panelFn2 <- panelFunctionGenerator("vanKrevelenPlot", colorCName="NOSC", vkBoundarySet="bs2", showVKBounds=TRUE)

makeDisplay(bySample, 
            panelFn=panelFn2,
            cogFn=vanKrevelenCognostics(vkBoundarySet="bs2"),
            name = "Van_Krevelen_plots_colored_by_NOSC",
            group = "Sample")
view()

# Next we will construct a Kendrick plot for each sample.

panelFn3 <- panelFunctionGenerator("kendrickPlot")

makeDisplay(bySample, 
            panelFn=panelFn3,
            cogFn=kendrickCognostics(),
            name = "Kendrick_plots_for_each_sample",
            group = "Sample")
view()

## Map peaks to MetaCyc
compound_data = mapPeaksToCompounds(pa_data)
