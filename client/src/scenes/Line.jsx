import Header from "../components/Header";
import {Box, Button, FormControl, MenuItem, Select} from "@mui/material";
import PieChart from "../components/PieChart";
import {useEffect, useState} from "react";
import {mockDistrictData} from "../data/MockData";

const Line = () => {

    return (
        <Box m="20px">
            <Header title="Line Chart" subtitle="Data Visualization for Velibs" />
        </Box>
    );
}

export default Line;