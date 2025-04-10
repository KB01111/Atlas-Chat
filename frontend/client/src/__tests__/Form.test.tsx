import React, { useState } from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

function TestForm() {
  const [value, setValue] = useState('');
  const [submitted, setSubmitted] = useState('');

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        setSubmitted(value);
      }}
    >
      <input placeholder="Type here" value={value} onChange={(e) => setValue(e.target.value)} />
      <button type="submit">Submit</button>
      {submitted && <div>Submitted: {submitted}</div>}
    </form>
  );
}

test('user can fill and submit the form', async () => {
  render(<TestForm />);
  const input = screen.getByPlaceholderText('Type here');
  await userEvent.type(input, 'Hello World');
  await userEvent.click(screen.getByText('Submit'));
  expect(screen.getByText('Submitted: Hello World')).toBeInTheDocument();
});
