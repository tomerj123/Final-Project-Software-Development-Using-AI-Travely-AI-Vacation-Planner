import { Card } from '@mui/material';
import { FC } from 'react';
import { SomeScreen2Layout } from './SomeScreen2Layout';

interface SomeScreen2Props {
    someProps: number;
}

export const SomeScreen2: FC<SomeScreen2Props> = (props) => {
    const { someProps } = props;

    return (
        <SomeScreen2Layout>
            <Card>000000000</Card>
            <Card>111111111</Card>
            <Card>222222222</Card>
            <Card>333333333</Card>
            <Card>444444444</Card>
            <Card>555555555</Card>
            <Card>666666666</Card>
            <Card>{someProps}</Card>
            <Card>8888888888888</Card>
            <Card>99999999999</Card>
        </SomeScreen2Layout>
    );
};
