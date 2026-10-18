namespace Beacon.Poc
{
    public static class WillMath
    {
        public static int Restore(int current, int gain, int capacity)
        {
            if (current < 0 || gain < 0 || capacity < 0)
                throw new System.ArgumentOutOfRangeException();
            return (int)System.Math.Min(capacity, (long)current + gain);
        }
    }
}
