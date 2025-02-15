import {gql} from '@apollo/client';
import * as React from 'react';
import styled from 'styled-components/macro';

import {PartitionGraph} from './PartitionGraph';
import {
  getPipelineDurationForRun,
  getPipelineExpectationFailureForRun,
  getPipelineExpectationRateForRun,
  getPipelineExpectationSuccessForRun,
  getPipelineMaterializationCountForRun,
  getStepDurationsForRun,
  getStepExpectationFailureForRun,
  getStepExpectationRateForRun,
  getStepExpectationSuccessForRun,
  getStepMaterializationCountForRun,
  PARTITION_GRAPH_FRAGMENT,
  StepSelector,
} from './PartitionGraphUtils';
import {PartitionGraphSetRunFragment} from './types/PartitionGraphSetRunFragment';

export const PartitionGraphSet: React.FC<{
  partitions: {name: string; runs: PartitionGraphSetRunFragment[]}[];
  allStepKeys: string[];
  isJob: boolean;
}> = ({partitions, allStepKeys, isJob}) => {
  const [hiddenStepKeys, setHiddenStepKeys] = React.useState<string[]>([]);
  const durationGraph = React.useRef<any>(undefined);
  const materializationGraph = React.useRef<any>(undefined);
  const successGraph = React.useRef<any>(undefined);
  const failureGraph = React.useRef<any>(undefined);
  const rateGraph = React.useRef<any>(undefined);
  const graphs = [durationGraph, materializationGraph, successGraph, failureGraph, rateGraph];

  const onChangeHiddenStepKeys = (hiddenKeys: string[]) => {
    setHiddenStepKeys(hiddenKeys);

    graphs.forEach((graph) => {
      const chart = graph?.current?.getChartInstance();
      const datasets = chart?.data?.datasets || [];
      datasets.forEach((dataset: any, idx: number) => {
        const meta = chart.getDatasetMeta(idx);
        meta.hidden = hiddenKeys.includes(dataset.label);
      });
    });
  };

  const runsByPartitionName = {};
  partitions.forEach((partition) => {
    runsByPartitionName[partition.name] = partition.runs;
  });

  return (
    <PartitionContentContainer>
      <StepSelector
        isJob={isJob}
        all={allStepKeys}
        hidden={hiddenStepKeys}
        onChangeHidden={onChangeHiddenStepKeys}
      />

      <div style={{flex: 1}}>
        <PartitionGraph
          isJob={isJob}
          title="Execution Time by Partition"
          yLabel="Execution time (secs)"
          runsByPartitionName={runsByPartitionName}
          getPipelineDataForRun={getPipelineDurationForRun}
          getStepDataForRun={getStepDurationsForRun}
          ref={durationGraph}
        />
        <PartitionGraph
          isJob={isJob}
          title="Materialization Count by Partition"
          yLabel="Number of materializations"
          runsByPartitionName={runsByPartitionName}
          getPipelineDataForRun={getPipelineMaterializationCountForRun}
          getStepDataForRun={getStepMaterializationCountForRun}
          ref={materializationGraph}
        />
        <PartitionGraph
          isJob={isJob}
          title="Expectation Successes by Partition"
          yLabel="Number of successes"
          runsByPartitionName={runsByPartitionName}
          getPipelineDataForRun={getPipelineExpectationSuccessForRun}
          getStepDataForRun={getStepExpectationSuccessForRun}
          ref={successGraph}
        />
        <PartitionGraph
          isJob={isJob}
          title="Expectation Failures by Partition"
          yLabel="Number of failures"
          runsByPartitionName={runsByPartitionName}
          getPipelineDataForRun={getPipelineExpectationFailureForRun}
          getStepDataForRun={getStepExpectationFailureForRun}
          ref={failureGraph}
        />
        <PartitionGraph
          isJob={isJob}
          title="Expectation Rate by Partition"
          yLabel="Rate of success"
          runsByPartitionName={runsByPartitionName}
          getPipelineDataForRun={getPipelineExpectationRateForRun}
          getStepDataForRun={getStepExpectationRateForRun}
          ref={rateGraph}
        />
      </div>
    </PartitionContentContainer>
  );
};

export const PARTITION_GRAPH_SET_RUN_FRAGMENT = gql`
  fragment PartitionGraphSetRunFragment on PipelineRun {
    id
    status
    tags {
      key
      value
    }
    ...PartitionGraphFragment
  }
  ${PARTITION_GRAPH_FRAGMENT}
`;

const PartitionContentContainer = styled.div`
  display: flex;
  flex-direction: row;
  position: relative;
  margin: 0 auto;
`;
