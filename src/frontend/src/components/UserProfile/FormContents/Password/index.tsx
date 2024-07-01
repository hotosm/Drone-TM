import { FormControl, Input, Label } from '@Components/common/FormUI';
import { FlexColumn } from '@Components/common/Layouts';

export default function PasswordSection() {
  return (
    <section className="naxatw-px-14 naxatw-py-10">
      <FlexColumn gap={5}>
        <FormControl>
          <Label required>Password</Label>
          <Input className="naxatw-mt-1" placeholder="Enter Password" />
        </FormControl>
        <FormControl>
          <Label required>Confirm Password</Label>
          <Input className="naxatw-mt-1" placeholder="Enter Password Again" />
        </FormControl>
      </FlexColumn>
    </section>
  );
}
