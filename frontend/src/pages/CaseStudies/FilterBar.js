
import React, { useState } from 'react';
import { Grid, TextField, FormControl, InputLabel, Select, MenuItem, Box, Autocomplete, InputAdornment, IconButton } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

const FilterBar = ({ availableTags, filters, onFilterChange }) => {
    const [searchTerm, setSearchTerm] = useState('');

    const handleMultiSelectChange = (name, newValue) => {
        onFilterChange(name, newValue);
    };

    const handleSearchSubmit = () => {
        if (searchTerm.trim() !== '') {
            onFilterChange('search', searchTerm.trim());
            setSearchTerm(''); // Clear search bar after submission
        }
    };

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
            handleSearchSubmit();
        }
    };

    return (
        <Box sx={{ mb: 4, p: 2, border: '1px solid #444', borderRadius: 1 }}>
            <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} md={4}>
                    <TextField
                        fullWidth
                        variant="outlined"
                        label="Search for keyword(s)..."
                        name="search"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        onKeyDown={handleKeyDown}
                        InputProps={{
                            endAdornment: (
                                <InputAdornment position="end">
                                    <IconButton onClick={handleSearchSubmit} edge="end">
                                        <SearchIcon />
                                    </IconButton>
                                </InputAdornment>
                            ),
                        }}
                    />
                </Grid>
                <Grid item xs={12} sm={4} md={2.6}>
                    <Autocomplete
                        multiple
                        options={availableTags.countries || []}
                        getOptionLabel={(option) => option}
                        value={filters.countries || []}
                        onChange={(event, newValue) => {
                            handleMultiSelectChange('countries', newValue);
                        }}
                        renderTags={() => null} // Prevent chips from appearing in the input field
                        renderInput={(params) => (
                            <TextField
                                {...params}
                                variant="outlined"
                                label="Countries"
                                placeholder="Countries"
                            />
                        )}
                    />
                </Grid>
                <Grid item xs={12} sm={4} md={2.6}>
                    <FormControl fullWidth>
                        <InputLabel>Industries</InputLabel>
                        <Select
                            multiple
                            name="industries"
                            value={filters.industries || []}
                            label="Industries"
                            onChange={(e) => handleMultiSelectChange('industries', e.target.value)}
                        >
                            {availableTags.industries?.map(i => <MenuItem key={i} value={i}>{i}</MenuItem>)}
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item xs={12} sm={4} md={2.6}>
                    <FormControl fullWidth>
                        <InputLabel>Pillars</InputLabel>
                        <Select
                            multiple
                            name="pillars"
                            value={filters.pillars || []}
                            label="Pillars"
                            onChange={(e) => handleMultiSelectChange('pillars', e.target.value)}
                        >
                            {availableTags.pillars?.map(p => <MenuItem key={p} value={p}>{p}</MenuItem>)}
                        </Select>
                    </FormControl>
                </Grid>
            </Grid>
        </Box>
    );
};

export default FilterBar;
