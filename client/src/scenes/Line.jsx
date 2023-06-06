import Header from "../components/Header";
import LineChart from "../components/PieChart";
import {useEffect, useState} from "react";
import {mockDistrictData} from "../data/MockData";
import {tokens} from "../theme";
import {
    useTheme,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogContentText,
    DialogActions,
    Button,
    Box, FormControl, Select, MenuItem
} from "@mui/material";
import PieChart from "../components/PieChart";
import {ResponsiveLine} from "@nivo/line";


const Line = () => {
    const theme = useTheme();
    const [districts, setDistricts] = useState([]);
    const [selectedDistrict, setSelectedDistrict] = useState('');
    const [data, setData] = useState([]);
    const [isGeneratingChart, setIsGeneratingChart] = useState(false);
    const [selectedTimePeriod, setSelectedTimePeriod] = useState('');
    const colors = tokens(theme.palette.mode);
    useEffect(() => {
        // Fetch districts
        const fetchDistricts = () => {
            setDistricts(mockDistrictData.map(district => district.district_name));
        };

        fetchDistricts();
    }, []);

    const handleTimePeriodSelection = (event) => {
        setSelectedTimePeriod(event.target.value);
    };

    const handleRestartChart = () => {
        setData([]);
        setSelectedDistrict('');
        setSelectedTimePeriod('');
    };
    function convertJSON(jsonData) {
        const result = [];
        const dataMap = new Map();

        function formatDate(dateString) {
            const date = new Date(dateString);
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            const formattedDate = `${day}-${month}-${year} ${hours}:${minutes}`;
            return formattedDate;
        }

        for (const item of jsonData) {
            const { id, total_available_bikes, x } = item;
            const formattedDate = formatDate(x);

            if (!dataMap.has(id)) {
                const data = {
                    id,
                    color: colors.greenAccent[500],
                    data: []
                };
                result.push(data);
                dataMap.set(id, data.data);
            }

            const data = {
                x: formattedDate,
                y: total_available_bikes
            };
            dataMap.get(id).push(data);
        }
        console.log(result);
        return result;
    }
    const fetchLineData = async (districtName, timePeriod) => {
            try {
                setIsGeneratingChart(true); // Set the flag to indicate chart generation in progress
                const response =  await fetch(`http://localhost:8800/station_status/bikes_count/${timePeriod}/${districtName}`);
                const jsonData =  await response.json();

                const convertedData = convertJSON(jsonData);

                setTimeout(() => {
                    setData(convertedData);
                    setIsGeneratingChart(false); // Set the flag to indicate chart generation completed
                }, 3000); // 3 seconds delay
            } catch (error) {
                console.error('Erreur lors de la récupération des données depuis l\'API:', error);
            }
        }


    return (
        <Box m="20px">
            <Header title="Line Chart" subtitle="Data visualization for Vélib'Métropole bikes" />
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
                        onClick={() => fetchLineData(selectedDistrict, selectedTimePeriod)}
                        variant="contained"
                    >
                        {isGeneratingChart ? 'Generating...' : 'Generate Chart'}
                    </Button>
                    <Button onClick={handleRestartChart} variant="contained">
                        Restart Chart
                    </Button>
                </div>
                {data.length > 0 && <ResponsiveLine
                    data={data}
                    margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
                    xScale={{ type: 'point' }}
                    yScale={{
                        type: 'linear',
                        min: 'auto',
                        max: 'auto',
                        stacked: true,
                        reverse: false
                    }}
                    yFormat=" >-.2f"
                    axisTop={null}
                    axisRight={null}
                    axisBottom={{
                        tickSize: 5,
                        tickPadding: 5,
                        tickRotation: 0,
                        legend: 'Date & Hour',
                        legendOffset: 36,
                        legendPosition: 'middle'
                    }}
                    axisLeft={{
                        tickSize: 5,
                        tickPadding: 5,
                        tickRotation: 0,
                        legend: 'Number of bikes',
                        legendOffset: -50,
                        legendPosition: 'middle'
                    }}
                    colors={{ scheme: 'paired' }}
                    pointSize={10}
                    pointColor={{ theme: 'background' }}
                    pointBorderWidth={2}
                    pointBorderColor={{ from: 'serieColor' }}
                    pointLabelYOffset={-12}
                    useMesh={true}
                    legends={[
                        {
                            anchor: 'bottom-right',
                            direction: 'column',
                            justify: false,
                            translateX: 82,
                            translateY: -45,
                            itemsSpacing: 0,
                            itemDirection: 'left-to-right',
                            itemWidth: 80,
                            itemHeight: 20,
                            itemOpacity: 0.75,
                            symbolSize: 12,
                            symbolShape: 'circle',
                            symbolBorderColor: 'rgba(0, 0, 0, .5)',
                            effects: [
                                {
                                    on: 'hover',
                                    style: {
                                        itemBackground: 'rgba(0, 0, 0, .03)',
                                        itemOpacity: 1
                                    }
                                }
                            ]
                        }
                    ]}
                />}
            </Box>
        </Box>
    );
}

export default Line;