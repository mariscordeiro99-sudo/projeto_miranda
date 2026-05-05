import React from "react";

type CardProps = React.HTMLAttributes<HTMLDivElement> & {
    title?: string;
    classTitle?: string;
    classCardHeader?: string;
    classCard?: string;
    classCardContent?: string;
    contentCard?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ title, classTitle, classCardHeader, classCard, classCardContent, contentCard, ...rest }) => {
    return (
        <div className={classCard} {...rest}>
            <div className={classCardHeader}>
                {title && <h3 className={classTitle}>{title}</h3>}
            </div>
            <div className={classCardContent}>
                {contentCard}
            </div>
        </div>
    );
};