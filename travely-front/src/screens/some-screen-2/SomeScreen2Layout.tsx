import { Grid } from '@mui/material';
import { FC } from 'react';

export const SomeScreen2Layout: FC<any> = ({ children }) => (
    <Grid container padding={2} spacing={1}>
        <Grid item xs={12} sm={12} md={12} lg={12}>
            {children[0]}
        </Grid>

        <Grid item xs={12} sm={12} md={12} lg={12}>
            {children[1]}
        </Grid>
        <Grid item container spacing={1}>
            <Grid item container spacing={1} xs={9} sm={9} md={9} lg={9}>
                <Grid item xs={3} sm={3} md={3} lg={3}>
                    {children[2]}
                </Grid>
                <Grid item xs={6} sm={6} md={6} lg={6}>
                    {children[3]}
                </Grid>
                <Grid item xs={3} sm={3} md={3} lg={3}>
                    {children[4]}
                </Grid>
                <Grid item xs={6} sm={6} md={6} lg={6}>
                    {children[5]}
                </Grid>
                <Grid item xs={6} sm={6} md={6} lg={6}>
                    {children[6]}
                </Grid>
                <Grid item xs={6} sm={6} md={6} lg={6}>
                    {children[7]}
                </Grid>
                <Grid item xs={6} sm={6} md={6} lg={6}>
                    {children[8]}
                </Grid>
            </Grid>
            <Grid item container xs={3} sm={3} md={3} lg={3}>
                <Grid item xs={12} sm={12} md={12} lg={12}>
                    {children[9]}
                </Grid>
            </Grid>
        </Grid>
    </Grid>
);
