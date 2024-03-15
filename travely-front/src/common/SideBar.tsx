import React from 'react';
import { Drawer, List, ListItem, ListItemIcon, ListItemText, Divider } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import FlightIcon from '@mui/icons-material/Flight';
import LoginIcon from '@mui/icons-material/Login';

const drawerWidth = 240;

export default function Sidebar() {
    return (
        <Drawer
            sx={{
                width: drawerWidth,
                flexShrink: 0,
                '& .MuiDrawer-paper': {
                    width: drawerWidth,
                    boxSizing: 'border-box',
                },
            }}
            variant="permanent"
            anchor="left"
        >
            <List>
                {/* Home Button */}
                <ListItem button key="Home">
                    <ListItemIcon>
                        <HomeIcon />
                    </ListItemIcon>
                    <ListItemText primary="Home" />
                </ListItem>

                {/* Saved Flights Button */}
                <ListItem button key="SavedTrips">
                    <ListItemIcon>
                        <FlightIcon />
                    </ListItemIcon>
                    <ListItemText primary="Saved Trips" />
                </ListItem>
            </List>
            <Divider />
            <List style={{ marginTop: 'auto' }}>
                {/* Login Button */}
                <ListItem button key="Login">
                    <ListItemIcon>
                        <LoginIcon />
                    </ListItemIcon>
                    <ListItemText primary="Login" />
                </ListItem>
            </List>
        </Drawer>
    );
}
