import { FormControl, Input, Label } from '@Components/common/FormUI';
import { FlexColumn } from '@Components/common/Layouts';

export default function OrganizationDetails() {
  return (
    <section className="naxatw-px-14 naxatw-py-10">
      <FlexColumn gap={5}>
        <FormControl>
          <Label required>Organization Name</Label>
          <Input
            placeholder="Enter Organization Name"
            className="naxatw-mt-1"
          />
        </FormControl>
        <FormControl>
          <Label required>Organization Address</Label>
          <Input
            placeholder="Enter Organization Address"
            className="naxatw-mt-1"
          />
        </FormControl>
        <FormControl>
          <Label required>Job Title</Label>
          <Input placeholder="Enter Job Title" className="naxatw-mt-1" />
        </FormControl>
      </FlexColumn>
    </section>
  );
}
