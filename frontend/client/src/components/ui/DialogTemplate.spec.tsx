import 'test/matchMedia.mock';
import { render, fireEvent } from '@testing-library/react';
import React from 'react';
import '@testing-library/jest-dom/extend-expect';
import { RecoilRoot } from 'recoil';

import DialogTemplate from './DialogTemplate';

import { Dialog } from '@radix-ui/react-dialog';

describe('DialogTemplate', () => {
  let mockSelectHandler;

  beforeEach(() => {
    mockSelectHandler = jest.fn();
  });

  it('renders correctly with all props', () => {
    const { getByText } = render(
      <RecoilRoot>
        <Dialog
          open
          data-testid="test-dialog"
          onOpenChange={() => {
            return;
          }}
        >
          <DialogTemplate
            title="Test Dialog"
            description="Test Description"
            main={<div>Main Content</div>}
            buttons={<button>Button</button>}
            leftButtons={<button>Left Button</button>}
            selection={{ selectHandler: mockSelectHandler, selectText: 'Select' }}
          />
        </Dialog>
      </RecoilRoot>,
    );

    expect(getByText('Test Dialog')).toBeInTheDocument();
    expect(getByText('Test Description')).toBeInTheDocument();
    expect(getByText('Main Content')).toBeInTheDocument();
    expect(getByText('Button')).toBeInTheDocument();
    expect(getByText('Left Button')).toBeInTheDocument();
    expect(getByText('Cancel')).toBeInTheDocument();
    expect(getByText('Select')).toBeInTheDocument();
  });

  it('renders correctly without optional props', () => {
    const { queryByText } = render(
      <RecoilRoot>
        <Dialog
          open
          onOpenChange={() => {
            return;
          }}
        />
      </RecoilRoot>,
    );

    expect(queryByText('Test Dialog')).toBeNull();
    expect(queryByText('Test Description')).not.toBeInTheDocument();
    expect(queryByText('Main Content')).not.toBeInTheDocument();
    expect(queryByText('Button')).not.toBeInTheDocument();
    expect(queryByText('Left Button')).not.toBeInTheDocument();
    expect(queryByText('Cancel')).not.toBeInTheDocument();
    expect(queryByText('Select')).not.toBeInTheDocument();
  });

  it('calls selectHandler when the select button is clicked', () => {
    const { getByText } = render(
      <RecoilRoot>
        <Dialog
          open
          onOpenChange={() => {
            return;
          }}
        >
          <DialogTemplate
            title="Test Dialog"
            selection={{ selectHandler: mockSelectHandler, selectText: 'Select' }}
          />
        </Dialog>
      </RecoilRoot>,
    );

    fireEvent.click(getByText('Select'));

    expect(mockSelectHandler).toHaveBeenCalled();
  });
});
