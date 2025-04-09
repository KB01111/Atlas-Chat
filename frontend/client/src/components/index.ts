import React from 'react';

export const OGDialog = ({ children }: { children?: React.ReactNode }) => <div>{children}</div>;

export const Button = ({ children }: { children?: React.ReactNode }) => <button>{children}</button>;

export const Spinner = () => <div>Loading...</div>;