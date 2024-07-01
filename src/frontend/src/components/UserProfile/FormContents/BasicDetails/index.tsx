import { Flex, FlexColumn } from '@Components/common/Layouts';
import { FormControl, Input, Label, Select } from '@Components/common/FormUI';

export default function BasicDetails() {
  return (
    <section className="naxatw-px-14 naxatw-py-10">
      <FlexColumn gap={5}>
        <Flex className="naxatw-h-14 naxatw-w-14 naxatw-items-center naxatw-justify-center naxatw-rounded-full naxatw-bg-grey-600">
          <h4>SK</h4>
        </Flex>
        <FormControl>
          <Label required>Name</Label>
          <Input placeholder="Enter Full Name" className="naxatw-mt-1" />
        </FormControl>
        <FormControl>
          <Label required>Country</Label>
          <Select
            options={[]}
            placeholder="Choose Country"
            className="naxatw-mt-1"
          />
        </FormControl>
        <FormControl>
          <Label required>City</Label>
          <Select
            options={[]}
            placeholder="Choose City"
            className="naxatw-mt-1"
          />
        </FormControl>
      </FlexColumn>
    </section>
  );
}
