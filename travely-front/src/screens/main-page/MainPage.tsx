import { Card } from '@mui/material';
import { FC } from 'react';
import { MainPageLayout } from './MainPageLayout';
import { TitleComponent } from './main-page-components/title/Title';
import Sidebar from '../../common/SideBar';
import { DescriptionComponent } from './main-page-components/title/Description';
import { InputComponent } from './main-page-components/title/InputContainer';

interface MainPageProps {
    someProps: number;
}

export const MainPage: FC<MainPageProps> = (props) => {
    const { someProps } = props;

    return (
        <MainPageLayout>
            <Sidebar />
            <TitleComponent />
            <DescriptionComponent />
            <InputComponent />
        </MainPageLayout>
    );
};
