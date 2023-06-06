import {
    Box,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle, FormControl, MenuItem, Select,
    useTheme
} from "@mui/material";
import Header from "../components/Header";
import {useEffect, useState} from "react";
import {tokens} from "../theme";
import {mockDistrictData} from "../data/MockData";
import {ResponsiveBar} from "@nivo/bar";
import PieChart from "../components/PieChart";

const Bar = () => {
    const theme = useTheme();
    const [districts, setDistricts] = useState([]);
    const [selectedDistrict, setSelectedDistrict] = useState('');
    const [isGeneratingChart, setIsGeneratingChart] = useState(false);
    const [selectedTimePeriod, setSelectedTimePeriod] = useState('');
    const [finalData, setFinalData] = useState([]);
    const [open, setOpen] = useState(false); // state pour contrôler l'ouverture du pop-up
    const [popupData, setPopupData] = useState(null); // state pour stocker les données du pop-up
    const colors = tokens(theme.palette.mode);
    useEffect(() => {
        // Fetch districts
        const fetchDistricts = () => {
            setDistricts(mockDistrictData.map(district => district.district_name));
        };

        fetchDistricts();
    }, []);


    const combineFetchedData = async (districtName, timePeriod) => {
        try {
            setIsGeneratingChart(true); // Set the flag to indicate chart generation in progress
            const url = `http://localhost:8800/station_status/districts/${timePeriod}/${districtName}`;
            const response = await fetch(url);
            const data = await response.json();
            setTimeout(() => {
                setFinalData(data);
                setIsGeneratingChart(false); // Set the flag to indicate chart generation completed
            }, 3000); // 3 seconds delay
        } catch (error) {
            console.error('Error fetching data: ', error);
            setIsGeneratingChart(false); // Set the flag to indicate chart generation completed with an error
        }
    };

    const handleTimePeriodSelection = (event) => {
        setSelectedTimePeriod(event.target.value);
    };

    const handleRestartChart = () => {
        setFinalData([]);
        setSelectedDistrict('');
        setSelectedTimePeriod('');
    };
    return (
        <Box m="20px">
            <Header title="Bar Chart" subtitle="Data Visualization for Velibs" />
            <Box height="75vh">
            <div>
                <FormControl>
                    <Select value={selectedDistrict} onChange={e => setSelectedDistrict(e.target.value)}>
                        <MenuItem value="">
                            <em>Select a district</em>
                        </MenuItem>
                        {districts.map(district => (
                            <MenuItem key={district} value={district}>{district}</MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <FormControl>
                    <Select value={selectedTimePeriod} onChange={handleTimePeriodSelection}>
                        <MenuItem value="">Select a time period</MenuItem>
                        <MenuItem value="realtime">Real-Time</MenuItem>
                        <MenuItem value="last_day">Last 24 Hours</MenuItem>
                        <MenuItem value="last_48_hours">Last 48 Hours</MenuItem>
                        <MenuItem value="last_72_hours">Last 72 Hours</MenuItem>
                        <MenuItem value="last_week">Last Week</MenuItem>
                    </Select>
                </FormControl>
                <Button
                    disabled={isGeneratingChart || !selectedTimePeriod}
                    onClick={() => combineFetchedData(selectedDistrict, selectedTimePeriod)}
                    variant="contained"
                >
                    {isGeneratingChart ? 'Generating...' : 'Generate Chart'}
                </Button>
                <Button onClick={handleRestartChart} variant="contained">
                    Restart Chart
                </Button>
            </div>
            {finalData.length > 0 &&
            <ResponsiveBar
                data={finalData}
                theme={{
                    // added
                    axis: {
                        domain: {
                            line: {
                                stroke: colors.grey[100],
                            },
                        },
                        legend: {
                            text: {
                                fill: colors.grey[100],
                            },
                        },
                        ticks: {
                            line: {
                                stroke: colors.grey[100],
                                strokeWidth: 1,
                            },
                            text: {
                                fill: colors.grey[100],
                            },
                        },
                    },
                    legends: {
                        text: {
                            fill: colors.grey[100],
                        },
                    },
                }}
                keys={["available_electric_bikes", "available_mechanical_bikes"]}
                indexBy="district_name"
                margin={{ top: 50, right: 130, bottom: 50, left: 60 }}
                padding={0.3}
                valueScale={{ type: "linear" }}
                indexScale={{ type: "band", round: true }}
                colors={{ scheme: "paired" }}
                defs={[
                    {
                        id: "dots",
                        type: "patternDots",
                        background: "inherit",
                        color: "#38bcb2",
                        size: 4,
                        padding: 1,
                        stagger: true,
                    },
                    {
                        id: "lines",
                        type: "patternLines",
                        background: "inherit",
                        color: "#eed312",
                        rotation: -45,
                        lineWidth: 6,
                        spacing: 10,
                    },
                ]}
                borderColor={{
                    from: "color",
                    modifiers: [["darker", "1.6"]],
                }}
                axisTop={null}
                axisRight={null}
                axisBottom={{
                    tickSize: 5,
                    tickPadding: 5,
                    tickRotation: 0,
                    legend: "Districts", // changed
                    legendPosition: "middle",
                    legendOffset: 32,
                }}
                axisLeft={{
                    tickSize: 5,
                    tickPadding: 5,
                    tickRotation: 0,
                    legend: "Availability", // changed
                    legendPosition: "middle",
                    legendOffset: -40,
                }}
                enableLabel={false}
                labelSkipWidth={12}
                labelSkipHeight={12}
                labelTextColor={{
                    from: "color",
                    modifiers: [["darker", 1.6]],
                }}
                legends={[
                    {
                        dataFrom: "keys",
                        anchor: "bottom-right",
                        direction: "column",
                        justify: false,
                        translateX: 120,
                        translateY: 0,
                        itemsSpacing: 2,
                        itemWidth: 100,
                        itemHeight: 20,
                        itemDirection: "left-to-right",
                        itemOpacity: 0.85,
                        symbolSize: 20,
                        effects: [
                            {
                                on: "hover",
                                style: {
                                    itemOpacity: 1,
                                },
                            },
                        ],
                    },
                ]}
                role="application"
                barAriaLabel={function (e) {
                    return e.id + ": " + e.formattedValue + " in stations: " + e.indexValue;
                }}
            />}
        </Box>

        </Box>
    );
}

export default Bar;