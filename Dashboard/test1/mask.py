
import operator

# See: http://www.cse.dmu.ac.uk/~eg/tele/CanbusIDandMask.html
ids = range(0x30b, 0x30b + 1) # Extended format example
#ids = range(0x581, 0x588 + 1) # Base format example

# Calculate CAN Bus filter and mask
FILTER = reduce(operator.and_, ids) # Simply bitwise AND all IDs together

MASK = reduce(operator.or_, ids) ^ FILTER # Get bits that are not constant among the IDs
# We can use all bits except these ones for the mask, so simply flip bits according to current format
if reduce(operator.or_, ids) > 0x7FF: # Check if using extended format
        MASK ^= 0x1FFFFFFF # Extended format = 29 bits
else:
        MASK ^= 0x7FF # Base format = 11 bits

# Just to make sure that it is calculated correctly
for id in ids:
     assert id & MASK == FILTER, 'Error: 0x' + format(id, 'X')

print 'Filter: 0x' + format(FILTER, 'X')
print 'Mask: 0x' + format(MASK, 'X')
