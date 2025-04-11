// ThemeSelector.spec.tsx
import 'test/matchMedia.mock';

import { render, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import '@testing-library/jest-dom/extend-expect';
import { RecoilRoot } from 'recoil';

import { ThemeSelector } from './General';

describe('ThemeSelector', () => {
  let mockOnChange;

  beforeEach(() => {
    mockOnChange = jest.fn();
  });

  it('renders correctly', () => {
    global.ResizeObserver = class MockedResizeObserver {
      observe = jest.fn();
      unobserve = jest.fn();
      disconnect = jest.fn();
    };
    const { getByText, getByRole } = render(
      <RecoilRoot>
        <ThemeSelector theme="system" onChange={mockOnChange} />
      </RecoilRoot>,
    );

    expect(getByText('Theme')).toBeInTheDocument();
    const dropdownButton = getByRole('combobox');
    expect(dropdownButton).toHaveTextContent('System');
  });

  it('calls onChange when the select value changes', async () => {
    global.ResizeObserver = class MockedResizeObserver {
      observe = jest.fn();
      unobserve = jest.fn();
      disconnect = jest.fn();
    };
    const { getByText, getByTestId } = render(
      <RecoilRoot>
        <ThemeSelector theme="system" onChange={mockOnChange} />
      </RecoilRoot>,
    );

    expect(getByText('Theme')).toBeInTheDocument();

    const dropdownButton = getByTestId('theme-selector');

    fireEvent.click(dropdownButton);

    const darkOption = getByText('Dark');
    fireEvent.click(darkOption);

    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalledWith('dark');
    });
  });
});
