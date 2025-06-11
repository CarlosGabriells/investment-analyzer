import fundData from '../../test/resultado_curl.json';
import { FundData } from './types';

export function getFundData(): FundData {
  return fundData as FundData;
}
