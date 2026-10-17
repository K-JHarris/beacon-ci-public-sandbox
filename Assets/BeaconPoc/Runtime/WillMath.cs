namespace Beacon.Poc
{
    public static class WillMath
    {
        public static int Restore(int current, int gain, int capacity)
        {
            if (current < 0 || gain < 0 || capacity < 0)
                throw new System.ArgumentOutOfRangeException();
            return System.Math.Min(capacity, (int)System.Math.Min(current + gain, int.MaxValue));
        }
    }
}
