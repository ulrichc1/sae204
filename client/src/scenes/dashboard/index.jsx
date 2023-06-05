import { Box, Button, IconButton, Typography, useTheme } from "@mui/material";
import { tokens } from "../../theme";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import EmailIcon from "@mui/icons-material/Email";
import PointOfSaleIcon from "@mui/icons-material/PointOfSale";
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import TrafficIcon from "@mui/icons-material/Traffic";
import Header from "../../components/Header";
import LineChart from "../../components/LineChart";
import GeographyChart from "../../components/GeographyChart";
import BarChart from "../../components/BarChart";
import StatBox from "../../components/StatBox";
import PieChart from "../../components/PieChart";
import {useEffect, useState} from "react";
import {mockDistrictData} from "../../data/MockData";
import {mockPieData} from '../../data/MockData';
const Dashboard = () => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [finalData, setFinalData] = useState([]);
    const [miniData, setMiniData] = useState([]);
    const [countDocks, setCountDocks] = useState('');
    const [countElectricBikes, setCountEbikes] = useState('');
    const [countMechanicalBikes, setCountMbikes] = useState('');
    const [countStations, setCountStations] = useState('');

    const lightGreenColor = "hsl(154,52%,45%)";
    const greenColor = "hsl(139,100%,83%)";


    // Fetch data for mechanical bikes
    const fetchMechanicalBikes = () => {
        const url = `http://localhost:8800/station_status/bikes/mechanical/forall`;
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
    const fetchElectronicBikes = () => {
        const url = `http://localhost:8800/station_status/bikes/electric/forall`;
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

    const combineFetchedData = async () => {
        try {
            const mechanicalData = await fetchMechanicalBikes();
            const electronicData = await fetchElectronicBikes();

            // Combine the two arrays into a single array
            const combinedData = [...mechanicalData, ...electronicData];

            setTimeout(() => {
                setFinalData(combinedData);
            }, 3000); // 3 seconds delay
        } catch (error) {
            console.error('Error fetching data: ', error);
        }
    }

    const fetchCountDocks = () => {
        const url = `http://localhost:8800/station_status/count_docks`;
        return fetch(url)
            .then(response => response.json())
            .then(data => {
                // Transform the fetched data and assign random colors
                return data.map(item => ({
                    id: `Count docks`,
                    value: item.count_docks,
                }));
            });
    }
    const fetchEbikes = () => {
        const url = `http://localhost:8800/station_status/count_ebikes`;
        return fetch(url)
            .then(response => response.json())
            .then(data => {
                // Transform the fetched data and assign random colors
                return data.map(item => ({
                    id: `Count Electric Bikes`,
                    value: item.count_ebikes,
                }));
            });
    }

    const fetchMbikes = () => {
        const url = `http://localhost:8800/station_status/count_mbikes`;
        return fetch(url)
            .then(response => response.json())
            .then(data => {
                // Transform the fetched data and assign random colors
                return data.map(item => ({
                    id: `Count Mechanical Bikes`,
                    value: item.count_mbikes,
                }));
            });
    }
    const fetchStations = () => {
        const url = `http://localhost:8800/station_status/status`;
        return fetch(url)
            .then(response => response.json())
            .then(data => {
                // Transform the fetched data and assign random colors
                return data.map(item => ({
                    id: `Count Stations`,
                    value: item.count_status,
                }));
            });
    }

    // Fusion des données (fetchStations, fetchMbikes, fetchEbikes, fetchCountDocks)

    const combineMiniData = async () => {
        try {
            const countDocks = await fetchCountDocks();
            const ebikes = await fetchEbikes();
            const mbikes = await fetchMbikes();
            const stations = await fetchStations();

            // Combine the two arrays into a single array
            const combined = [...countDocks, ...ebikes, ...mbikes, ...stations];

            setTimeout(() => {
                setMiniData(combined);
            }, 3000); // 3 seconds delay
            console.log(miniData);
        } catch (error) {
            console.error('Error fetching data: ', error);
        }
    }

    // Appel de la fonction combineFetchedData
    useEffect(() => {
        console.log('Fetching data...');
            combineFetchedData();
            // Si les données ont été récupérées, on les affiche dans la console
            if (finalData.length > 0) {
                console.log('Data fetched: ', finalData);
            }

    }
    , []);


    useEffect(() => {
        console.log('Fetching data...');
        combineMiniData();
        // Si les données ont été récupérées, on les affiche dans la console
        if (miniData.length > 0) {
            console.log('Combined data fetched: ', miniData);
            // Extraire les valeurs des identifiants dans des variables distinctes
            setCountDocks(miniData.find(item => item.label === "Count docks")?.value.toString());
            setCountEbikes(miniData.find(item => item.label === "Count Electric Bikes")?.value.toString());
            setCountMbikes(miniData.find(item => item.label === "Count Mechanical Bikes")?.value.toString());
            setCountStations(miniData.find(item => item.label === "Count Stations")?.value.toString());

            console.log(countDocks);
            console.log(countElectricBikes);
            console.log(countMechanicalBikes);
            console.log(countStations);
        }
    }, []);

    return (
        <Box m="20px">
            {/* HEADER */}
            <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Header title="Analyse Velibs Métropole" subtitle={"Mise à jour: " + new Date().toLocaleString() + ""} />
            </Box>

            {/* GRID & CHARTS */}
            <Box
                display="grid"
                gridTemplateColumns="repeat(12, 1fr)"
                gridAutoRows="140px"
                gap="20px"
            >
                {/* ROW 1 */}
                <Box
                    gridColumn="span 8"
                    gridRow="span 2"
                    backgroundColor={colors.primary[400]}
                >
                    <Box
                        mt="25px"
                        p="0 30px"
                        display="flex "
                        justifyContent="space-between"
                        alignItems="center"
                    >
                        <Box>
                            <Typography
                                variant="h5"
                                fontWeight="600"
                                color={colors.grey[100]}
                            >
                                Line Chart (Evolution)
                            </Typography>
                            <Typography
                                variant="h3"
                                fontWeight="bold"
                                color={colors.greenAccent[500]}
                            >
                            </Typography>
                        </Box>
                        <Box>
                        </Box>
                    </Box>
                    <Box height="250px" m="-20px 0 0 0">
                        <LineChart isDashboard={true} />
                    </Box>
                </Box>

                {/* ROW 3 */}
                <Box
                    gridColumn="span 4"
                    gridRow="span 2"
                    backgroundColor={colors.primary[400]}
                    p="30px"
                >
                    <Typography variant="h5" fontWeight="600">
                        Pie Chart
                    </Typography>
                    <Box height="250px" m="-20px 0 0 0">
                        <PieChart isDashboard={true} data={finalData}/>
                    </Box>
                </Box>
                <Box
                    gridColumn="span 12"
                    gridRow="span 2"
                    backgroundColor={colors.primary[400]}
                >
                    <Typography
                        variant="h5"
                        fontWeight="600"
                        sx={{ padding: "30px 30px 0 30px" }}
                    >
                        Bar Chart
                    </Typography>
                    <Box height="250px" mt="-20px">
                        <BarChart isDashboard={true} />
                    </Box>
                </Box>
            </Box>
        </Box>

    );
};

export default Dashboard;