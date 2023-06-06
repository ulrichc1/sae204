import { Box, List, ListItem, ListItemButton, ListItemText, Button, FormControl, Select, MenuItem } from "@mui/material";
import Header from "../components/Header";
import PieChart from "../components/PieChart";
import { useEffect, useState } from "react";
import { mockDistrictData } from "../data/MockData";

const Pie = () => {
    const [districts, setDistricts] = useState([]);
    const [selectedDistrict, setSelectedDistrict] = useState('');
    const [finalData, setFinalData] = useState([]);
    const lightGreenColor = "hsl(154,52%,45%)";
    const greenColor = "hsl(139,100%,83%)";
    const [isGeneratingChart, setIsGeneratingChart] = useState(false);
    const [selectedTimePeriod, setSelectedTimePeriod] = useState('');


    const addTwoHours = (dateString) => {
        const [date, time] = dateString.split("T"); // Split into date and time components
        const [hour, rest] = time.split(":"); // Split the time into hour and the rest of the time components

        let modifiedHour = parseInt(hour, 10); // Convert hour to an integer
        modifiedHour += 2; // Add 2 hours
        modifiedHour = modifiedHour.toString().padStart(2, "0"); // Convert modified hour back to a two-digit string

        const modifiedTime = `${modifiedHour}:${rest}`; // Combine the modified hour with the rest of the time components

        const formattedDate = `${date} ${modifiedTime}`; // Combine the modified date and time components

        return formattedDate;
    };

    // Fetch data for mechanical bikes
    const fetchMechanicalBikes = (districtName, timePeriod) => {
        const url = `http://localhost:8800/station_status/bikes/mechanical/${timePeriod}/${districtName}`;
        return fetch(url)
            .then(response => response.json())
            .then(data => {
                // Transform the fetched data and assign random colors
                return data.map(i => ({
                    id: `Mechanical bikes`,
                    label: `Mechanical bikes`,
                    value: i.value,
                    color: lightGreenColor
                }));
            });
    };

    // Fetch data for electronic bikes
    const fetchElectronicBikes = (districtName, timePeriod) => {
        const url = `http://localhost:8800/station_status/bikes/electric/${timePeriod}/${districtName}`;
        return fetch(url)
            .then(response => response.json())
            .then(data => {
                // Transform the fetched data and assign random colors
                return data.map(item => ({
                    id: `Electronic bikes`,
                    label: `Electronic bikes`,
                    value: item.value,
                    color: greenColor
                }));
            });
    };

    const combineFetchedData = async (districtName, timePeriod) => {
        try {
            setIsGeneratingChart(true); // Set the flag to indicate chart generation in progress
            const mechanicalData = await fetchMechanicalBikes(districtName, timePeriod);
            const electronicData = await fetchElectronicBikes(districtName, timePeriod);

            // Combine the two arrays into a single array
            const combinedData = [...mechanicalData, ...electronicData];

            setTimeout(() => {
                setFinalData(combinedData);
                setIsGeneratingChart(false); // Set the flag to indicate chart generation completed
            }, 3000); // 3 seconds delay
        } catch (error) {
            console.error('Error fetching data: ', error);
            setIsGeneratingChart(false); // Set the flag to indicate chart generation completed with an error
        }
    };

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
        setFinalData([]);
        setSelectedDistrict('');
        setSelectedTimePeriod('');
    };

    return (
        <Box m="20px">
            <Header title="Pie Chart" subtitle="Electric Bikes & Mechanical Bikes" />
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
                {finalData.length > 0 && <PieChart data={finalData} />}
            </Box>
        </Box>
    );
};

export default Pie;
